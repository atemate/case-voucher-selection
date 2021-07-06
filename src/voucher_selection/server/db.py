import logging
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Optional, Union

import psycopg2
from psycopg2.extensions import connection as Connection

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


@dataclass
class VoucherSelectionParameters:
    """Contains parameters that can be used for choosing the voucher:
    - country_code: full match
    - total_orders_from and total_orders_to: defines frequency_segment
    - last_order_from and last_order_to: defines recency_segment
    """

    country_code: Optional[str] = None
    total_orders_from: Optional[int] = None
    total_orders_to: Optional[int] = None
    last_order_from: Optional[str] = None
    last_order_to: Optional[str] = None

    def to_where_clause(self):
        # TODO: test
        constraints = []
        if self.country_code:
            constraints.append(f"country_code = '{self.country_code}'")
        if self.last_order_from and self.last_order_to:
            constraints.append(
                f"last_order_ts >= (NOW() - INTERVAL '{self.last_order_to} days')"
            )
            constraints.append(
                f"last_order_ts <= (NOW() - INTERVAL '{self.last_order_from} days')"
            )
        if self.total_orders_from and self.total_orders_to:
            constraints.append(f"total_orders >= {self.total_orders_from}")
            constraints.append(f"total_orders <= {self.total_orders_to}")
        return " AND ".join(constraints)


def get_connection(config: DBConfig):
    return psycopg2.connect(config.url)


def get_db(db_config: DBConfig):
    return get_db_by_connection(get_connection(db_config))


@contextmanager
def get_db_by_connection(db_connection):
    with DBManager(conn=db_connection) as db:
        yield db


class DBManager:
    def __init__(self, conn: Connection):
        self._conn = conn
        self._table = "voucher_selection"

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self._conn.close()

    @property
    def table(self) -> str:
        return self._table

    def get_cursor(self) -> Connection:
        return self._conn.cursor()

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
        self.create_table()
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

    def get_voucher_amount(
        self,
        params: VoucherSelectionParameters,
    ):
        where_clause = params.to_where_clause()
        if where_clause:
            where_clause = f"WHERE {where_clause}"
        with self._conn.cursor() as cur:
            sql = dedent(
                f"""\
                SELECT
                    COUNT(DISTINCT(voucher_amount)), AVG(DISTINCT(voucher_amount))
                FROM {self.table}
                {where_clause}
                """
            )
            cur.execute(sql)
            found = cur.fetchone()
            count, value = found
            if count == 0:
                return None
            value = int(value)
            logger.info(
                f"Found {count} distinct voucher values for `{where_clause}`: mean={value}"
            )
            return value
            # # Or explicitly:
            # logger.debug(f"Result:\n" + "\n".join(str(row) for row in found))
            # vouchers = list({row[-1] for row in found})
            # result = int(sum(vouchers) / len(vouchers))
            # logger.info(
            #     f"Found {len(vouchers)} elements for constraint `{where_clause}``:\n{vouchers}\n=> mean={result}"
            # )
            # return result
