import logging
from contextlib import contextmanager
from pathlib import Path
from textwrap import dedent
from typing import Optional, Union

import psycopg2
from psycopg2.extensions import connection

from ..data_cleaning import load_csv
from .config import DBConfig


logger = logging.getLogger()
DB_COLUMNS = {
    "timestamp": "DATE",
    "country_code": "VARCHAR",
    "last_order_ts": "DATE",
    "first_order_ts": "DATE",
    "total_orders": "INT",
    "voucher_amount": "INT",
}


def get_connection(config: DBConfig):
    return psycopg2.connect(config.url)


@contextmanager
def get_db(db_config: DBConfig):
    with DBManager(conn=get_connection(db_config)) as db:
        yield db


class DBManager:
    def __init__(self, conn: connection):
        self._conn = conn
        self._table = "voucher_selection"

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self._conn.close()

    @property
    def table(self) -> str:
        return self._table

    def create_table(self):
        columns = ", ".join(f"{k} {v}" for k, v in DB_COLUMNS.items())
        sql = dedent(
            f"""\
            CREATE TABLE IF NOT EXISTS {self.table} (
                id serial PRIMARY KEY, {columns}
            )
            """
        )
        with self._conn.cursor() as cur:
            cur.execute(sql)
            self._conn.commit()

    def insert_from_csv(self, csv_path: Union[str, Path]):
        df = load_csv(csv_path)
        size = df.shape[0]

        columns = ", ".join(DB_COLUMNS)
        with self._conn.cursor() as cur:
            logger.info(f"Building the query of {size} rows")
            values = [tupl[1] for tupl in df.iterrows()]
            values = [tuple(str(v) for v in row) for row in values]
            values_template = ",".join(["%s"] * len(values))
            sql = dedent(
                f"""\
                INSERT INTO {self.table} ({columns})
                VALUES {values_template}
                """
            )
            logger.info(f"Executing the query")
            cur.execute(sql, values)
            self._conn.commit()

        logger.info(f"Successfully inserted {size} rows from {csv_path}")

    def select_voucher_amount(
        self,
        country_code: Optional[str] = None,
        last_order_from: Optional[str] = None,
        last_order_to: Optional[str] = None,
        total_orders_from: Optional[int] = None,
        total_orders_to: Optional[int] = None,
    ):
        constraints = ["1=1"]
        if country_code:
            constraints.append(f"country_code = '{country_code}'")
        if last_order_from and last_order_to:
            constraints.append(f"last_order_ts >= (NOW() - INTERVAL '{last_order_to} days')")
            constraints.append(f"last_order_ts <= (NOW() - INTERVAL '{last_order_from} days')")
        if total_orders_from and total_orders_to:
            constraints.append(f"total_orders >= {total_orders_from}")
            constraints.append(f"total_orders <= {total_orders_to}")
        where_clause = " AND ".join(constraints)

        with self._conn.cursor() as cur:
            sql = dedent(
                f"""\
                SELECT
                    COUNT(DISTINCT(voucher_amount)), AVG(DISTINCT(voucher_amount))
                FROM {self.table}
                WHERE {where_clause}
                """
            )
            cur.execute(sql)
            found = cur.fetchone()
            if not found:
                return None
            count, value = found
            value = int(value)
            logger.info(f"Found {count} distinct voucher values, mean: {value}")
            return value
            ## Or explicitly:
            # logger.debug(f"Result:\n" + "\n".join(str(row) for row in found))
            # vouchers = list({row[-1] for row in found})
            # result = int(sum(vouchers) / len(vouchers))
            # logger.info(
            #     f"Found {len(vouchers)} elements for constraint `{where_clause}``:\n{vouchers}\n=> mean={result}"
            # )
            # return result

    # def select_all(self):
    #     with self._conn.cursor() as cur:
    #         sql = f"SELECT * FROM {self.table}"
    #         cur.execute(sql)
    #         exists = cur.fetchmany()
    #         print(exists)
    #         return exists
