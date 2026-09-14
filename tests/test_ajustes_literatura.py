import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ajustes_literatura import house_effect_lookup, house_effect_vote, house_effect_stats, temporal_projection


def test_house_effect_prefers_institute_candidate_bias():
    df = pd.DataFrame(
        [
            {"instituto": "A", "candidato": "X", "voto_valido_estimado": 40, "resultado_real_validos": 45},
            {"instituto": "A", "candidato": "X", "voto_valido_estimado": 41, "resultado_real_validos": 46},
            {"instituto": "A", "candidato": "X", "voto_valido_estimado": 42, "resultado_real_validos": 47},
        ]
    )

    lookup = house_effect_lookup(house_effect_stats(df, min_rows=3))

    assert house_effect_vote({"instituto": "A", "candidato": "X", "voto_valido_estimado": 50}, lookup) == 55


def test_temporal_projection_caps_recent_trend():
    df = pd.DataFrame(
        [
            {"data_publicacao": "2026-09-01", "voto_valido_estimado": 40, "amostra": 1000},
            {"data_publicacao": "2026-09-11", "voto_valido_estimado": 50, "amostra": 1000},
        ]
    )

    assert temporal_projection(df, "2026-10-04") == 50
