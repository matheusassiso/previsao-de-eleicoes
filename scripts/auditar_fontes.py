from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
PESQUISAS = PROCESSED / "pesquisas_validos.csv"
OUT = PROCESSED / "auditoria_fontes.csv"


def audit_sources(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["amostra"] = pd.to_numeric(data["amostra"], errors="coerce")
    data["voto_valido_estimado"] = pd.to_numeric(data["voto_valido_estimado"], errors="coerce")
    rows = []
    for (year, source), group in data.groupby(["ano_eleicao", "fonte"], dropna=False):
        polls = group.drop_duplicates(["instituto", "data_publicacao", "cenario"])
        rows.append(
            {
                "ano_eleicao": int(year),
                "fonte": source,
                "linhas": len(group),
                "pesquisas_unicas": len(polls),
                "institutos": group["instituto"].nunique(),
                "amostra_missing": int(group["amostra"].isna().sum()),
                "amostra_imputada": int(pd.to_numeric(group.get("amostra_imputada", 0), errors="coerce").fillna(0).sum()),
                "valor_fora_0_100": int(((group["voto_valido_estimado"] < 0) | (group["voto_valido_estimado"] > 100)).sum()),
                "primeira_publicacao": str(pd.to_datetime(group["data_publicacao"]).min().date()),
                "ultima_publicacao": str(pd.to_datetime(group["data_publicacao"]).max().date()),
            }
        )
    return pd.DataFrame(rows).sort_values(["ano_eleicao", "fonte"])


def demo() -> None:
    df = pd.DataFrame(
        [
            {"ano_eleicao": 2002, "fonte": "x", "instituto": "A", "data_publicacao": "2002-09-01", "cenario": "nacional", "amostra": None, "amostra_imputada": 1, "voto_valido_estimado": 40},
            {"ano_eleicao": 2002, "fonte": "x", "instituto": "A", "data_publicacao": "2002-09-01", "cenario": "nacional", "amostra": 1000, "amostra_imputada": 0, "voto_valido_estimado": 101},
        ]
    )
    result = audit_sources(df)
    assert int(result.iloc[0]["amostra_missing"]) == 1
    assert int(result.iloc[0]["valor_fora_0_100"]) == 1


def main() -> None:
    demo()
    result = audit_sources(pd.read_csv(PESQUISAS))
    result.to_csv(OUT, index=False)
    print(f"{len(result)} linhas gravadas em {OUT}")


if __name__ == "__main__":
    main()
