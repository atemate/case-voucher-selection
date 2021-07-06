import re
from contextlib import contextmanager
from enum import Enum
from typing import Optional, Tuple

from .config import DBConfig
from .db import DBManager, get_db


PATTERN_SEGMENT_INTERVAL = re.compile(r"^(\d+)-(\d+)$")


def parse_segment_interval(value: str) -> Tuple[int, int]:
    match = PATTERN_SEGMENT_INTERVAL.search(value)
    if match is None:
        e = f"Invalid segment interval '{value}'"
        raise ValueError(f"{e}: does not match pattern {PATTERN_SEGMENT_INTERVAL}")
    a, b = int(match.group(1)), int(match.group(2))
    return a, b


@contextmanager
def get_svc(db_config: DBConfig):
    with get_db(db_config) as db:
        yield VoucherSelectionService(db)


class VoucherSelectionService:
    def __init__(self, db: DBManager):
        self._db = db

    def compute_voucher_amount(
        self,
        customer_id: Optional[int] = None,
        country_code: Optional[str] = None,
        last_order_ts: Optional[str] = None,
        first_order_ts: Optional[str] = None,
        total_orders: Optional[int] = None,
        frequency_segment: Optional[str] = None,
        recency_segment: Optional[str] = None,
    ):
        if frequency_segment:
            total_from, total_to = parse_segment_interval(frequency_segment)
        else:
            total_from, total_to = None, None

        if recency_segment:
            last_from, last_to = parse_segment_interval(recency_segment)
        else:
            last_from, last_to = None, None

        return self._db.select_voucher_amount(
            country_code=country_code,
            last_order_from=last_from,
            last_order_to=last_to,
            total_orders_from=total_from,
            total_orders_to=total_to,
        )
