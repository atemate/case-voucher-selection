import logging
from typing import Optional

import pandas as pd


logger = logging.getLogger(__file__)

ORDER_COLUMNS = [
    "timestamp",
    "country_code",
    "last_order_ts",
    "first_order_ts",
    "total_orders",
    "voucher_amount",
]


def convert_str_to_int(value: Optional[str]) -> int:
    value_str = value or "0.0"
    value_float = float(value_str)
    if not value_float.is_integer():
        raise ValueError(f"Not an integer: {value_float}")
    value_int = int(value_float)
    return value_int


def clean_orders_raw(data: pd.DataFrame) -> pd.DataFrame:
    """
    Returns the cleaned copy of the dataframe with the following transformations:

    - Make sure the dataset contains only columns we need (see `ORDER_COLUMNS`)
    - Convert timestamps to `datetime`
    - Fix the column `total_orders`:
        - use value `0.0` instead of empty strings
        - convert all values to `int`
    - Fix the column `voucher_amount`:
        - use value `0` instead of NaN
        - convert all values to `int`

    For more details, see jupyter notebooks `<project>/notebooks`.
    """
    logger.info(f"Cleaning raw dataset of size: {data.size}")
    df = data.copy(deep=True)
    df = df[ORDER_COLUMNS]

    for col in ["timestamp", "first_order_ts", "last_order_ts"]:
        df[col] = pd.to_datetime(df[col])

    df["total_orders"] = df["total_orders"].fillna(0).apply(convert_str_to_int)
    df["voucher_amount"] = df["voucher_amount"].fillna(0).apply(convert_str_to_int)

    return df
