from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from bayesiano_dinamico import daily_series, fit_latent_forecast, forecast


def test_kalman_latent_forecast_returns_interval():
    series = pd.Series([30, 31, 32, 33], index=pd.date_range("2026-09-01", periods=4, freq="D"))
    estimate, low, high, method = fit_latent_forecast(series, date(2026, 9, 8))

    assert method == "kalman_local_level"
    assert low <= estimate <= high


def test_forecast_uses_only_available_polls():
    polls = pd.DataFrame(
        [
            {"ano_eleicao": 2026, "turno": 1, "data_publicacao": "2026-09-01", "cenario_rotulo": "A", "candidato": "X", "voto_valido_estimado": 40, "amostra": 1000, "usar_previsao_principal": 1},
            {"ano_eleicao": 2026, "turno": 1, "data_publicacao": "2026-09-05", "cenario_rotulo": "A", "candidato": "X", "voto_valido_estimado": 90, "amostra": 1000, "usar_previsao_principal": 1},
            {"ano_eleicao": 2026, "turno": 1, "data_publicacao": "2026-09-01", "cenario_rotulo": "A", "candidato": "Y", "voto_valido_estimado": 60, "amostra": 1000, "usar_previsao_principal": 1},
        ]
    )
    elections = pd.DataFrame([{"ano_eleicao": 2026, "data_primeiro_turno": "2026-10-04"}])

    result = forecast(polls, elections, forecast_date=date(2026, 9, 1))

    assert not result.empty
    assert float(result[result["candidato"] == "X"].iloc[0]["voto_valido_estimado"]) == 40


def test_daily_series_uses_sample_weight():
    polls = pd.DataFrame(
        [
            {"data_publicacao": "2026-09-01", "voto_valido_estimado": 40, "amostra": 100},
            {"data_publicacao": "2026-09-01", "voto_valido_estimado": 50, "amostra": 1600},
        ]
    )

    series = daily_series(polls)

    assert round(float(series.iloc[0]), 2) == 48.0


def test_forecast_excludes_float_zero_principal_flag():
    polls = pd.DataFrame(
        [
            {"ano_eleicao": 2026, "turno": 1, "data_publicacao": "2026-09-01", "cenario_rotulo": "A", "candidato": "X", "voto_valido_estimado": 40, "amostra": 1000, "usar_previsao_principal": 1.0},
            {"ano_eleicao": 2026, "turno": 1, "data_publicacao": "2026-09-01", "cenario_rotulo": "B", "candidato": "X", "voto_valido_estimado": 80, "amostra": 1000, "usar_previsao_principal": 0.0},
        ]
    )
    elections = pd.DataFrame([{"ano_eleicao": 2026, "data_primeiro_turno": "2026-10-04"}])

    result = forecast(polls, elections, forecast_date=date(2026, 9, 1))

    assert set(result["cenario"]) == {"A"}
