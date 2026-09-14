from __future__ import annotations

import csv
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DOCS = ROOT / "docs"
ELEICOES = RAW / "eleicoes.csv"
OUT = RAW / "fundamentos_eleicao.csv"
REPORT = DOCS / "coleta-fundamentos.md"

INDICATORS = {
    "pib_crescimento": "NY.GDP.MKTP.KD.ZG",
    "inflacao": "FP.CPI.TOTL.ZG",
    "desemprego": "SL.UEM.TOTL.ZS",
}


def fetch_indicator(indicator: str) -> dict[int, float]:
    url = f"https://api.worldbank.org/v2/country/BRA/indicator/{indicator}?format=json&per_page=200"
    with urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    return {int(row["date"]): float(row["value"]) for row in rows if row.get("value") is not None}


def pick_latest_before(values: dict[int, float], election_year: int) -> tuple[int | None, float | None]:
    years = [year for year in values if year < election_year]
    if not years:
        return None, None
    year = max(years)
    return year, values[year]


def election_years() -> list[int]:
    with ELEICOES.open(newline="", encoding="utf-8") as file:
        return [int(row["ano_eleicao"]) for row in csv.DictReader(file)]


def build_rows() -> list[dict[str, str]]:
    series = {name: fetch_indicator(code) for name, code in INDICATORS.items()}
    rows = []
    for year in election_years():
        row = {"ano_eleicao": str(year), "fonte": "World Bank API"}
        ref_years = []
        for name, values in series.items():
            ref_year, value = pick_latest_before(values, year)
            row[name] = "" if value is None else f"{value:.4f}"
            row[f"{name}_ano"] = "" if ref_year is None else str(ref_year)
            if ref_year is not None:
                ref_years.append(ref_year)
        row["fundamentos_ano_referencia"] = "" if not ref_years else str(min(ref_years))
        row["fundamentos_defasagem_max"] = "" if not ref_years else str(year - min(ref_years))
        rows.append(row)
    return rows


def write_rows(rows: list[dict[str, str]]) -> None:
    fields = [
        "ano_eleicao",
        "pib_crescimento",
        "pib_crescimento_ano",
        "inflacao",
        "inflacao_ano",
        "desemprego",
        "desemprego_ano",
        "fundamentos_ano_referencia",
        "fundamentos_defasagem_max",
        "fonte",
    ]
    RAW.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    REPORT.write_text(
        "\n".join(
            [
                "# Coleta de fundamentos economicos",
                "",
                "- Fonte: World Bank API, Brasil.",
                "- Indicadores: crescimento real do PIB, inflacao ao consumidor e desemprego.",
                "- Regra anti-vazamento: para cada eleicao, usar apenas o ultimo ano disponivel anterior ao ano eleitoral.",
                f"- Linhas geradas: {len(rows)}.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def demo() -> None:
    assert pick_latest_before({2020: 1.0, 2022: 2.0}, 2022) == (2020, 1.0)


def main() -> None:
    demo()
    rows = build_rows()
    write_rows(rows)
    print(f"{len(rows)} linhas gravadas em {OUT}")
    print(f"auditoria gravada em {REPORT}")


if __name__ == "__main__":
    main()
