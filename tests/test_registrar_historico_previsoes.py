import pandas as pd

from scripts.registrar_historico_previsoes import update_history


def test_update_history_replaces_same_snapshot():
    current = pd.DataFrame(
        [
            {"data_previsao": "2026-09-01", "ano_eleicao": 2026, "cenario": "A", "modelo": "m", "candidato": "X", "voto_valido_estimado": 42},
        ]
    )
    history = pd.DataFrame(
        [
            {"data_previsao": "2026-09-01", "ano_eleicao": 2026, "cenario": "A", "modelo": "m", "candidato": "X", "voto_valido_estimado": 41},
        ]
    )

    history["data_registro"] = "old"
    out = update_history(current, history, data_registro="new")

    assert len(out) == 2
    assert set(out["data_registro"]) == {"old", "new"}
