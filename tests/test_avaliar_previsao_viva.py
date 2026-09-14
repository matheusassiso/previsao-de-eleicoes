import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from avaliar_previsao_viva import simulate_live_forecast


def test_live_forecast_uses_only_polls_available_by_cutoff():
    rows = pd.DataFrame(
        [
            {"ano_eleicao": 2022, "cenario": "a", "candidato": "A", "data_publicacao": "2022-08-01", "dias_publicacao_ate_eleicao": 62, "amostra": 1000, "voto_valido_estimado": 40, "resultado_real_validos": 45},
            {"ano_eleicao": 2022, "cenario": "a", "candidato": "A", "data_publicacao": "2022-09-20", "dias_publicacao_ate_eleicao": 12, "amostra": 1000, "voto_valido_estimado": 50, "resultado_real_validos": 45},
            {"ano_eleicao": 2022, "cenario": "a", "candidato": "B", "data_publicacao": "2022-08-01", "dias_publicacao_ate_eleicao": 62, "amostra": 1000, "voto_valido_estimado": 30, "resultado_real_validos": 35},
            {"ano_eleicao": 2022, "cenario": "a", "candidato": "B", "data_publicacao": "2022-09-20", "dias_publicacao_ate_eleicao": 12, "amostra": 1000, "voto_valido_estimado": 20, "resultado_real_validos": 35},
        ]
    )

    result = simulate_live_forecast(rows, [60])

    assert set(result["modelo"]) == {"baseline_pesquisa", "baseline_ajustado", "baseline_efeito_casa", "baseline_temporal", "bayesiano_dinamico_kalman"}
    assert set(result["dias_antes_eleicao"]) == {60}
    assert result[result["modelo"] == "baseline_pesquisa"].iloc[0]["mae"] == 5
