from pathlib import Path

from voucher_selection.server.db import DBManager


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
