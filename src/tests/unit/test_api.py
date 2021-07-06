from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient
from psycopg2.extensions import connection as Connection

from voucher_selection.server.api import get_api_by_connection
from voucher_selection.server.db import get_db_by_connection


@pytest.fixture
def client(postgresql: Connection, sql_file: Path) -> Iterator[TestClient]:
    with get_db_by_connection(postgresql) as db:
        db.insert_from_csv(sql_file)

        api = get_api_by_connection(postgresql)
        with TestClient(api) as client:
            yield client


def test_api_ping(client: TestClient):
    r = client.get("/ping")
    assert r.status_code == 200, r.text
    assert r.json() == {"ping": "pong"}


def test_api_voucher_invalid_missing_arguments(client: TestClient):
    r = client.post("/voucher")
    assert r.status_code == 422, r.text
    assert r.json() == {
        "detail": [
            {"loc": ["body"], "msg": "field required", "type": "value_error.missing"}
        ]
    }


def test_api_voucher_invalid_wrong_path(client: TestClient):
    r = client.get("/wrongpath")
    assert r.status_code == 404, r.text


def test_api_voucher_invalid_wrong_method(client: TestClient):
    r = client.get("/voucher")
    assert r.status_code == 405, r.text


def test_api_voucher_ok_country_code(client: TestClient):
    r = client.post("/voucher", json={"country_code": "Latvia"})
    assert r.status_code == 200, r.text
    assert r.json() == {"voucher_amount": 5940}


def test_api_voucher_empty_wrong_country_code(client: TestClient):
    r = client.post("/voucher", json={"country_code": "InVaLiD"})
    assert r.status_code == 204, r.text
    assert r.json() is None


def test_api_voucher_ok_frequency_segment(client: TestClient):
    r = client.post("/voucher", json={"frequency_segment": "1-3"})
    assert r.status_code == 200, r.text
    assert r.json() == {"voucher_amount": 5720}


def test_api_voucher_ok_country_code_and_frequency_segment(client: TestClient):
    r = client.post(
        "/voucher", json={"country_code": "Latvia", "frequency_segment": "1-3"}
    )
    assert r.status_code == 200, r.text
    assert r.json() == {"voucher_amount": 8800}


def test_api_voucher_ok_country_code_and_recency_segment(
    client: TestClient, postgresql
):
    # TODO: freeze the time and test it properly
    r = client.post(
        "/voucher", json={"country_code": "Latvia", "recency_segment": "10000-20000"}
    )
    assert r.status_code == 204, r.text
    assert r.json() is None


def test_api_voucher_ok_recency_segment(client: TestClient, postgresql):
    # TODO: freeze the time and test it properly
    r = client.post("/voucher", json={"recency_segment": "10000-20000"})
    assert r.status_code == 204, r.text
    assert r.json() is None
