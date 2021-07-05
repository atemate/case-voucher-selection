import io

import pandas as pd
import pandas.api.types as ptypes
import pytest

from voucher_selection.data_cleaning import (
    ORDER_COLUMNS,
    clean_orders_raw,
    convert_str_to_int,
)


ORDERS_RAW_TEXT = """
timestamp	country_code	last_order_ts	first_order_ts	total_orders	voucher_amount
0	2020-05-20 15:43:38.364972+00:00	China	2020-04-19 00:00:00+00:00	2020-04-18 00:00:00+00:00	0.0	5720.0
1	2020-05-20 15:43:47.914346+00:00	Latvia	2020-04-19 00:00:00+00:00	2020-04-13 00:00:00+00:00	1.0
2	2020-05-20 15:36:56.866239+00:00	China	2020-04-19 00:00:00+00:00	2020-04-15 00:00:00+00:00	""	1760.0
3	2020-05-20 15:00:33.694108+00:00	Brazil	2020-04-19 00:00:00+00:00	2020-04-13 00:00:00+00:00		1762.0
4	2020-05-20 15:43:18.521402+00:00	China	2020-04-19 00:00:00+00:00	2020-04-14 00:00:00+00:00	3.0
"""


@pytest.fixture
def orders_raw() -> pd.DataFrame:
    return pd.read_csv(io.StringIO(ORDERS_RAW_TEXT), delimiter="\t")


def test_convert_str_to_int_empty_string():
    value = ""
    assert convert_str_to_int(value) == 0


def test_convert_str_to_int_none():
    value = None
    assert convert_str_to_int(value) == 0


def test_convert_str_to_int_valid_float_zero():
    value = "0.0"
    assert convert_str_to_int(value) == 0


def test_convert_str_to_int_valid_float_non_zero():
    value = "10.0"
    assert convert_str_to_int(value) == 10


@pytest.mark.parametrize(
    "value",
    [
        "10.1",
        "10,1",
        "10e-14",
        "invalid",
    ],
)
def test_convert_str_to_int_invalid_string(value: str):
    with pytest.raises(ValueError):
        convert_str_to_int(value)


def test_clean_orders_raw_correct_size(orders_raw: pd.DataFrame):
    df = clean_orders_raw(orders_raw)
    assert df.size == orders_raw.size
    assert list(df.columns) == ORDER_COLUMNS


def test_clean_orders_raw_correct_no_nans(orders_raw: pd.DataFrame):
    df = clean_orders_raw(orders_raw)
    assert df["timestamp"].isna().sum() == 0
    assert df["last_order_ts"].isna().sum() == 0
    assert df["first_order_ts"].isna().sum() == 0
    assert df["total_orders"].isna().sum() == 0
    assert df["voucher_amount"].isna().sum() == 0


def test_clean_orders_raw_correct_dtypes(orders_raw: pd.DataFrame):
    df = clean_orders_raw(orders_raw)
    assert ptypes.is_datetime64_any_dtype(df["timestamp"])
    assert ptypes.is_datetime64_any_dtype(df["last_order_ts"])
    assert ptypes.is_datetime64_any_dtype(df["first_order_ts"])
    assert ptypes.is_integer_dtype(df["total_orders"])
    assert ptypes.is_integer_dtype(df["voucher_amount"])
