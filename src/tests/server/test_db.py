import tempfile
from pathlib import Path

import pytest

from voucher_selection.server.db import DBManager


TEST_CSV_DATA = """\
timestamp,country_code,last_order_ts,first_order_ts,total_orders,voucher_amount
2020-05-20 15:43:38.364972+00:00,China,2020-04-19 00:00:00+00:00,2020-04-18 00:00:00+00:00,0,5720
2020-05-20 15:43:47.914346+00:00,Latvia,2020-04-19 00:00:00+00:00,2020-04-13 00:00:00+00:00,1,8800
2020-05-20 15:24:04.621986+00:00,Peru,2020-04-19 00:00:00+00:00,2017-07-24 00:00:00+00:00,2,2640
"""


class TestPostgresQueryManager:
    @pytest.fixture
    def sql_file(self) -> Path:
        tmp = Path(tempfile.mktemp())
        tmp.write_text(TEST_CSV_DATA)
        return tmp

    def test_create_table_twice(self, postgresql):
        m = DBManager(postgresql)
        for _ in range(2):
            m.create_table()
            with postgresql.cursor() as cur:
                cur.execute(
                    f"SELECT EXISTS (SELECT FROM information_schema.tables "
                    f"WHERE table_name='{m.table}')"
                )
                exists = cur.fetchone()[0]
                assert exists, "Table was not created"

    def test_insert_from_csv(self, postgresql, sql_file: Path):
        m = DBManager(postgresql)
        m.create_table()
        m.insert_from_csv(sql_file)
        with postgresql.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {m.table}")
            count = cur.fetchone()[0]
            assert count == 3, "Table was not created"
