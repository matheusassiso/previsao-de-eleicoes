import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gerar_ensemble import combine_forecasts, compute_weights


def test_combine_forecasts_uses_accepted_model_weights():
    forecasts = pd.DataFrame(
        [
            {"data_previsao": "2026-01-01", "ano_eleicao": 2026, "cenario": "A", "candidato": "X", "modelo": "m1", "voto_valido_estimado": 40, "probabilidade_liderar": 0.2, "probabilidade_ir_ao_segundo_turno": 1, "fonte_dados_ate": "2026-01-01"},
            {"data_previsao": "2026-01-01", "ano_eleicao": 2026, "cenario": "A", "candidato": "X", "modelo": "m2", "voto_valido_estimado": 50, "probabilidade_liderar": 0.8, "probabilidade_ir_ao_segundo_turno": 1, "fonte_dados_ate": "2026-01-01"},
            {"data_previsao": "2026-01-01", "ano_eleicao": 2026, "cenario": "A", "candidato": "X", "modelo": "m3", "voto_valido_estimado": 90, "probabilidade_liderar": 1.0, "probabilidade_ir_ao_segundo_turno": 1, "fonte_dados_ate": "2026-01-01"},
        ]
    )
    weights = pd.DataFrame({"modelo": ["m1", "m2"], "peso": [0.25, 0.75]})

    out = combine_forecasts(forecasts, weights)

    assert out.iloc[0]["voto_valido_estimado"] == 47.5
    assert round(float(out.iloc[0]["probabilidade_liderar"]), 2) == 0.65


def test_weights_can_promote_bayesian_from_live_backtest():
    backtest = pd.DataFrame({"modelo": ["baseline_pesquisa"], "mae": [6]})
    live = pd.DataFrame({"modelo": ["baseline_pesquisa", "bayesiano_dinamico_kalman"], "mae": [8, 7]})

    weights = compute_weights(backtest, live)

    assert "bayesiano_dinamico_kalman" in set(weights["modelo"])
