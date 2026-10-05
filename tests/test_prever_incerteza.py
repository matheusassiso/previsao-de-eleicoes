import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prever import forecast, interval_width


def test_forecast_uses_calibrated_probabilities_and_intervals():
    rows = [
        {"ano_eleicao": "2026", "turno": "1", "data_publicacao": "2026-09-01", "amostra": "1000", "cenario": "A", "candidato": "A", "voto_valido_estimado": "51"},
        {"ano_eleicao": "2026", "turno": "1", "data_publicacao": "2026-09-01", "amostra": "1000", "cenario": "A", "candidato": "B", "voto_valido_estimado": "49"},
    ]

    result = forecast(rows, date(2026, 9, 2), calibration={"baseline_pesquisa": 5})
    leader = [row for row in result if row["modelo"] == "baseline_pesquisa" and row["candidato"] == "A"][0]

    assert float(leader["probabilidade_liderar"]) < 1
    assert round(float(leader["intervalo_alto"]) - float(leader["voto_valido_estimado"]), 4) == interval_width("baseline_pesquisa", {"baseline_pesquisa": 5})
    assert "baseline_temporal" in {row["modelo"] for row in result}


def test_forecast_normalizes_valid_votes_by_scenario_and_model():
    rows = [
        {"ano_eleicao": "2026", "turno": "1", "data_publicacao": "2026-09-01", "amostra": "1000", "cenario": "A", "candidato": "A", "voto_valido_estimado": "60"},
        {"ano_eleicao": "2026", "turno": "1", "data_publicacao": "2026-09-01", "amostra": "1000", "cenario": "A", "candidato": "B", "voto_valido_estimado": "60"},
    ]

    result = forecast(rows, date(2026, 9, 2), calibration={"baseline_pesquisa": 5})
    by_model = {}
    for row in result:
        by_model.setdefault(row["modelo"], 0.0)
        by_model[row["modelo"]] += float(row["voto_valido_estimado"])

    assert round(by_model["baseline_pesquisa"], 4) == 100.0
    assert round(by_model["baseline_temporal"], 4) == 100.0
