import logging
import os
from datetime import datetime
from time import time
from typing import Optional

import pydantic
import uvicorn
from fastapi import Depends, FastAPI, HTTPException

from .config import DBConfig
from .db import DBManager, get_db
from .voucher_service import get_svc


logger = logging.getLogger()


class CustomerInput(pydantic.BaseModel):
    customer_id: Optional[int] = None
    country_code: Optional[str] = None
    last_order_ts: Optional[str] = None
    first_order_ts: Optional[str] = None
    total_orders: Optional[int] = None
    frequency_segment: Optional[str] = None
    recency_segment: Optional[str] = None


def get_api(db_config: DBConfig) -> FastAPI:
    api = FastAPI()

    def _get_svc():
        with get_svc(db_config) as svc:
            yield svc

    @api.get("/ping")
    def ping():
        return {"ping": "pong"}

    @api.post("/voucher")
    async def post_voucher(input: CustomerInput, svc: DBManager = Depends(_get_svc)):
        try:
            voucher = svc.compute_voucher_amount(
                customer_id=input.customer_id,
                country_code=input.country_code,
                last_order_ts=input.last_order_ts,
                first_order_ts=input.first_order_ts,
                total_orders=input.total_orders,
                frequency_segment=input.frequency_segment,
                recency_segment=input.recency_segment,
            )
            return voucher

        except BaseException as e:
            detail = f"Unexpected error: {e}"
            logger.exception(detail)
            raise HTTPException(status_code=500, detail=detail)

    return api


if __name__ == "__run__":
    run()
