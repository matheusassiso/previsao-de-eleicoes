from __future__ import annotations

from pathlib import Path
from datetime import datetime

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
ATUAL = PROCESSED / "previsao_ensemble.csv"
HISTORICO = PROCESSED / "previsoes_historico.csv"
KEY = ["data_registro", "data_previsao", "ano_eleicao", "cenario", "modelo", "candidato"]


def update_history(current: pd.DataFrame, history: pd.DataFrame | None = None, data_registro: str | None = None) -> pd.DataFrame:
    snapshot = current.copy()
    snapshot["data_registro"] = data_registro or datetime.now().isoformat(timespec="seconds")
    frames = [snapshot]
    if history is not None and not history.empty:
        frames.insert(0, history.copy())
    out = pd.concat(frames, ignore_index=True)
    return out.drop_duplicates(KEY, keep="last").sort_values(KEY)


def demo() -> None:
    current = pd.DataFrame(
        [
            {"data_previsao": "2026-09-01", "ano_eleicao": 2026, "cenario": "A", "modelo": "m", "candidato": "X", "voto_valido_estimado": 41},
            {"data_previsao": "2026-09-02", "ano_eleicao": 2026, "cenario": "A", "modelo": "m", "candidato": "X", "voto_valido_estimado": 42},
        ]
    )
    history = pd.DataFrame([current.iloc[0].to_dict() | {"data_registro": "old", "voto_valido_estimado": 40}])
    out = update_history(current, history, data_registro="new")
    assert len(out) == 3
    assert set(out["data_registro"]) == {"old", "new"}


def main() -> None:
    demo()
    current = pd.read_csv(ATUAL) if ATUAL.exists() else pd.DataFrame()
    history = pd.read_csv(HISTORICO) if HISTORICO.exists() else pd.DataFrame()
    updated = update_history(current, history)
    updated.to_csv(HISTORICO, index=False)
    print(f"{len(updated)} linhas gravadas em {HISTORICO}")


if __name__ == "__main__":
    main()
