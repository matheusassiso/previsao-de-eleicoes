from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from coletar_2002_uol import parse_number, parse_poll_dates


def test_parse_poll_dates_handles_ranges():
    assert parse_poll_dates("4-5/out/02") == ("2002-10-04", "2002-10-05")
    assert parse_poll_dates("31/jul a 1/ago/02") == ("2002-07-31", "2002-08-01")


def test_parse_number_handles_commas_and_missing():
    assert parse_number("40,6") == 40.6
    assert parse_number("n.d.") is None
