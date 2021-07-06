from pathlib import Path

import psycopg2.errors
import pytest

from voucher_selection.server.db import DBManager, VoucherSelectionParameters


def test_create_table_twice(db: DBManager):
    for _ in range(2):
        db.create_table()
        with db.get_cursor() as cur:
            cur.execute(
                f"SELECT EXISTS (SELECT FROM information_schema.tables "
                f"WHERE table_name='{db.table}')"
            )
            exists = cur.fetchone()[0]
            assert exists, "Table was not created"


def test_insert_from_csv(db: DBManager, sql_file: Path):
    db.create_table()
    db.insert_from_csv(sql_file)
    with db.get_cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {db.table}")
        count = cur.fetchone()[0]
        assert count == 8


def test_get_voucher_amount_ok_country_code(db: DBManager, sql_file: Path):
    db.create_table()
    db.insert_from_csv(sql_file)

    params = VoucherSelectionParameters(country_code="China")
    voucher = db.get_voucher_amount(params)
    assert voucher == 2493


def test_get_voucher_amount_ok_frequency_segment(db: DBManager, sql_file: Path):
    db.create_table()
    db.insert_from_csv(sql_file)

    params = VoucherSelectionParameters(total_orders_from=1, total_orders_to=1)
    voucher = db.get_voucher_amount(params)
    assert voucher == 8800


def test_get_voucher_amount_ok_recency_segment(db: DBManager, sql_file: Path):
    db.create_table()
    db.insert_from_csv(sql_file)

    params = VoucherSelectionParameters(last_order_from=1, last_order_to=2)
    voucher = db.get_voucher_amount(params)
    assert voucher is None


def test_get_voucher_amount_invalid_recency_segment_out_of_range(
    db: DBManager, sql_file: Path
):
    db.create_table()
    db.insert_from_csv(sql_file)

    params = VoucherSelectionParameters(last_order_from=1, last_order_to=100000000)
    with pytest.raises(
        psycopg2.errors.DatetimeFieldOverflow, match="timestamp out of range"
    ):
        db.get_voucher_amount(params)


def test_get_voucher_amount_ok_multiple_params(db: DBManager, sql_file: Path):
    db.create_table()
    db.insert_from_csv(sql_file)

    params = VoucherSelectionParameters(
        country_code="Latvia",
        total_orders_from=1,
        total_orders_to=2,
        last_order_from=0,
        last_order_to=100000,
    )
    voucher = db.get_voucher_amount(params)
    assert voucher == 8800
