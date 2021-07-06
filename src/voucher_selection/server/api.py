import logging
import re
from typing import Optional, Tuple

import pydantic
from fastapi import Depends, FastAPI, HTTPException

from .config import DBConfig
from .db import DBManager, VoucherSelectionParameters, get_db


logger = logging.getLogger("api")

PATTERN_SEGMENT_INTERVAL = re.compile(r"^(\d+)-(\d+)$")


class CustomerInput(pydantic.BaseModel):
    customer_id: Optional[int] = None
    country_code: Optional[str] = None
    last_order_ts: Optional[str] = None
    first_order_ts: Optional[str] = None
    total_orders: Optional[int] = None
    frequency_segment: Optional[str] = None
    recency_segment: Optional[str] = None


def parse_segment_interval(value: str) -> Tuple[int, int]:
    match = PATTERN_SEGMENT_INTERVAL.search(str(value))
    if match is None:
        e = f"Invalid segment interval '{value}'"
        raise ValueError(f"{e}: does not match pattern {PATTERN_SEGMENT_INTERVAL}")
    a, b = int(match.group(1)), int(match.group(2))
    return a, b


def build_voucher_selection_params(input: CustomerInput) -> VoucherSelectionParameters:
    # TODO: tests
    country_code = input.country_code

    fs = input.frequency_segment
    if fs:
        total_orders_from, total_orders_to = parse_segment_interval(fs)
    else:
        total_orders_from, total_orders_to = None, None

    rs = input.recency_segment
    if rs:
        last_order_from, last_order_to = parse_segment_interval(rs)
    else:
        last_order_from, last_order_to = None, None

    return VoucherSelectionParameters(
        country_code=country_code,
        total_orders_from=total_orders_from,
        total_orders_to=total_orders_to,
        last_order_from=last_order_from,
        last_order_to=last_order_to,
    )


def get_api(db_config: DBConfig) -> FastAPI:
    api = FastAPI()

    def _get_db():
        with get_db(db_config) as db:
            yield db

    @api.get("/ping")
    def ping():
        return {"ping": "pong"}

    @api.post("/voucher")
    async def post_voucher(input: CustomerInput, db: DBManager = Depends(_get_db)):
        try:
            params = build_voucher_selection_params(input)
            voucher = db.get_voucher_amount(params)
            return voucher
        except BaseException as e:
            detail = f"Unexpected error: {e}"
            logger.exception(detail)
            raise HTTPException(status_code=500, detail=detail)

    return api
