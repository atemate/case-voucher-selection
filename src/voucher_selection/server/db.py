import logging
from pathlib import Path
from textwrap import dedent
from typing import Union

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


class DBManager:
    def __init__(self, conn: connection):
        self._conn = conn
        self._table = "voucher_selection"

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
