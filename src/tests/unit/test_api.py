from typing import Tuple

import pytest

from voucher_selection.server.api import parse_segment_interval


@pytest.mark.parametrize(
    "value,expected",
    [
        ("0-0", (0, 0)),
        ("0-10", (0, 10)),
        ("10-100", (10, 100)),
        ("100-100", (100, 100)),
    ],
)
def test_parse_segment_interval_ok(value: str, expected: Tuple[int, int]):
    assert parse_segment_interval(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        None,
        "invalid",
        "0-",
        "abc2-3",
        "2-3def",
    ],
)
def test_parse_segment_interval_invalid(value: str):
    with pytest.raises(ValueError):
        parse_segment_interval(value)
