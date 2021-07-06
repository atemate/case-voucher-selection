import tempfile
from pathlib import Path

import pytest

from voucher_selection.server.db import DBManager, get_db_by_connection


TEST_CSV_DATA = """\
timestamp,country_code,last_order_ts,first_order_ts,total_orders,voucher_amount
2020-05-20 15:43:38.364972+00:00,China,2020-04-19 00:00:00+00:00,2020-04-18 00:00:00+00:00,0,5720
2020-05-20 15:43:47.914346+00:00,Latvia,2020-04-19 00:00:00+00:00,2020-04-13 00:00:00+00:00,1,8800
2020-05-20 15:45:45.018547+00:00,Latvia,2020-04-19 00:00:00+00:00,2019-12-29 00:00:00+00:00,0,3080
2020-05-20 15:24:04.621986+00:00,Peru,2020-04-19 00:00:00+00:00,2017-07-24 00:00:00+00:00,2,2640
2020-05-20 14:32:03.085178+00:00,China,2020-04-19 00:00:00+00:00,2019-07-25 00:00:00+00:00,0,0
2020-05-20 15:02:29.692047+00:00,Peru,2020-04-19 00:00:00+00:00,2019-03-04 00:00:00+00:00,47,2640
2020-05-20 15:36:42.336700+00:00,China,2020-04-19 00:00:00+00:00,2020-01-15 00:00:00+00:00,4,1760
2020-05-20 15:00:51.497972+00:00,Australia,2020-04-19 00:00:00+00:00,2020-01-25 00:00:00+00:00,82,2200
"""


@pytest.fixture
def sql_file() -> Path:
    tmp = Path(tempfile.mktemp())
    tmp.write_text(TEST_CSV_DATA)
    return tmp


@pytest.fixture
def db(postgresql) -> DBManager:
    with get_db_by_connection(postgresql) as db:
        yield db
