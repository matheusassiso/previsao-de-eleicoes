import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from coletar_fundamentos import pick_latest_before


def test_pick_latest_before_never_uses_election_year_or_future():
    values = {2024: 3.2, 2025: 2.1, 2026: 9.9}

    year, value = pick_latest_before(values, 2026)

    assert year == 2025
    assert value == 2.1
