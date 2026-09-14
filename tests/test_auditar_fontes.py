from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from auditar_fontes import audit_sources


def test_audit_sources_flags_basic_quality_issues():
    df = pd.DataFrame(
        [
            {"ano_eleicao": 1998, "fonte": "fonte_a", "instituto": "X", "data_publicacao": "1998-09-01", "cenario": "nacional", "amostra": None, "amostra_imputada": 1, "voto_valido_estimado": 20},
            {"ano_eleicao": 1998, "fonte": "fonte_a", "instituto": "X", "data_publicacao": "1998-09-01", "cenario": "nacional", "amostra": 1000, "amostra_imputada": 0, "voto_valido_estimado": 120},
        ]
    )

    result = audit_sources(df)

    assert int(result.iloc[0]["pesquisas_unicas"]) == 1
    assert int(result.iloc[0]["amostra_missing"]) == 1
    assert int(result.iloc[0]["valor_fora_0_100"]) == 1
