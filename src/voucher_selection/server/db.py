# import pandas as pd
from pathlib import Path
from textwrap import dedent
from typing import Union

from psycopg2.extensions import connection

# from databases import Database
# from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine
from .config import DBConfig


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
        if not csv_path.exists():
            raise FileNotFoundError(csv_path)

        columns = ", ".join(DB_COLUMNS)
        sql = dedent(
            f"""\
            COPY {self.table} (
                {columns}
            )
            FROM '{csv_path}'
            DELIMITER ','
            CSV HEADER;
            """
        )
        with self._conn.cursor() as cur:
            cur.execute(sql)
            self._conn.commit()
