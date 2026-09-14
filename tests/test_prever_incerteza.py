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
