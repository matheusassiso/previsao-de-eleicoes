from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DOCS = ROOT / "docs"
IN = RAW / "pesquisas_historicas_normalizadas.csv"
OUT = RAW / "pesquisas_historicas_limpas.csv"
REPORT = DOCS / "auditoria-limpeza-pesquisas.md"

FIRST_ROUND_TABLES = {
    2010: {"wikipedia_tabela_1"},
    2014: {"wikipedia_tabela_9"},
    2018: {"wikipedia_tabela_1"},
    2022: {f"wikipedia_tabela_{i}" for i in range(2, 9)},
    2026: {f"wikipedia_tabela_{i}" for i in range(2, 8)},
}

GROUP_FIELDS = ["ano_eleicao", "instituto", "data_fim_campo", "cenario"]


def load() -> pd.DataFrame:
    df = pd.read_csv(IN)
    df["ano_eleicao"] = pd.to_numeric(df["ano_eleicao"], errors="coerce").astype("Int64")
    df["amostra"] = pd.to_numeric(df["amostra"], errors="coerce").fillna(0)
    df["percentual_total"] = pd.to_numeric(df["percentual_total"], errors="coerce")
    df["indecisos"] = pd.to_numeric(df["indecisos"], errors="coerce").fillna(0)
    return df.dropna(subset=["ano_eleicao", "percentual_total"])


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    lines = [f"# Auditoria da limpeza de pesquisas", ""]
    lines.append(f"- Linhas normalizadas de entrada: {len(df)}.")

    allowed = df.apply(lambda row: row["cenario"] in FIRST_ROUND_TABLES.get(int(row["ano_eleicao"]), set()), axis=1)
    df = df[allowed].copy()
    lines.append(f"- Depois de manter apenas tabelas de primeiro turno: {len(df)}.")

    df["amostra_imputada"] = (df["amostra"] <= 0).astype(int)
    df.loc[df["amostra"] <= 0, "amostra"] = 1000
    lines.append(f"- Pesquisas sem amostra positiva receberam amostra imputada de 1000: {int(df['amostra_imputada'].sum())}.")

    groups = df.groupby(GROUP_FIELDS)["percentual_total"]
    sums = groups.transform("sum")
    counts = groups.transform("count")
    max_share = groups.transform("max")
    df = df[(sums >= 45) & (sums <= 100) & (counts >= 2) & (max_share <= 70)].copy()
    lines.append(f"- Depois de exigir cenario plausivel: soma entre 45 e 100, pelo menos 2 candidatos e nenhum candidato acima de 70: {len(df)}.")

    df["qualidade_fonte"] = "wikipedia_estruturada_auditoria_parcial"
    df["cenario_tipo"] = "primeiro_turno"
    counts = df.groupby("ano_eleicao").size()
    lines.append("")
    lines.append("## Linhas limpas por ano")
    for year, count in counts.items():
        lines.append(f"- {year}: {count}.")
    return df, lines


def demo() -> None:
    assert "wikipedia_tabela_1" in FIRST_ROUND_TABLES[2018]
    assert "wikipedia_tabela_7" not in FIRST_ROUND_TABLES[2018]


def main() -> None:
    demo()
    df, lines = clean(load())
    df.to_csv(OUT, index=False)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(df)} linhas gravadas em {OUT}")
    print(f"auditoria gravada em {REPORT}")


if __name__ == "__main__":
    main()
