from __future__ import annotations

from io import StringIO
from pathlib import Path
import re

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = RAW / "pesquisas_historicas_wikipedia.csv"
LOG = ROOT / "docs" / "coleta-pesquisas-wikipedia.md"

PAGES = {
    2026: "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Brazilian_presidential_election",
    2022: "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2022_Brazilian_presidential_election",
    2018: "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2018_Brazilian_presidential_election",
    2014: "https://en.wikipedia.org/wiki/2014_Brazilian_general_election",
    2010: "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2010_Brazilian_presidential_election",
}

CANDIDATES = {
    2026: ["Lula", "Flávio Bolsonaro", "Augusto Cury", "Renan Santos", "Ronaldo Caiado", "Romeu Zema", "Pablo Marçal"],
    2022: ["Lula", "Bolsonaro", "Gomes", "Tebet"],
    2018: ["Bolsonaro", "Haddad", "Ciro", "Alckmin", "Amoêdo", "Marina"],
    2014: ["Dilma", "Aécio", "Marina", "Luciana Genro", "Pastor Everaldo", "Eduardo Jorge"],
    2010: ["Dilma", "Serra", "Marina", "Plínio"],
}


def clean_column_name(column) -> str:
    if isinstance(column, tuple):
        column = " ".join(str(part) for part in column if "Unnamed" not in str(part))
    return re.sub(r"\s+", " ", str(column)).strip()


def parse_percent(value) -> float | None:
    text = str(value).replace("%", "").replace(",", ".").strip()
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group(0)) if match else None


def find_column(columns: list[str], options: list[str]) -> str | None:
    lowered = {column.lower(): column for column in columns}
    for option in options:
        for lower, original in lowered.items():
            if option.lower() in lower:
                return original
    return None


def candidate_column(columns: list[str], candidate: str) -> str | None:
    aliases = {
        "Lula": ["lula"],
        "Bolsonaro": ["bolsonaro"],
        "Flávio Bolsonaro": ["f. bolsonaro", "flávio", "flavio"],
        "Gomes": ["gomes", "ciro"],
        "Ciro": ["ciro", "gomes"],
        "Tebet": ["tebet"],
        "Dilma": ["dilma", "rousseff"],
        "Aécio": ["aécio", "aecio", "neves"],
        "Haddad": ["haddad"],
        "Serra": ["serra"],
        "Marina": ["marina"],
        "Alckmin": ["alckmin"],
        "Amoêdo": ["amoêdo", "amoedo"],
        "Plínio": ["plínio", "plinio"],
        "Luciana Genro": ["luciana"],
        "Pastor Everaldo": ["everaldo"],
        "Eduardo Jorge": ["eduardo"],
        "Augusto Cury": ["cury"],
        "Renan Santos": ["renan"],
        "Ronaldo Caiado": ["caiado"],
        "Romeu Zema": ["zema"],
        "Pablo Marçal": ["marçal", "marcal"],
    }
    for alias in aliases.get(candidate, [candidate]):
        found = find_column(columns, [alias])
        if found:
            return found
    return None


def table_to_rows(year: int, table: pd.DataFrame, index: int, url: str) -> list[dict[str, object]]:
    table = table.copy()
    table.columns = [clean_column_name(column) for column in table.columns]
    columns = list(table.columns)
    pollster_col = find_column(columns, ["publisher/pollster", "pollster/client", "polling firm", "polling firm/link", "pollster", "firm", "source", "institute"])
    date_col = find_column(columns, ["polling period", "date(s) administered", "date(s) conducted", "fieldwork", "last update", "date"])
    sample_col = find_column(columns, ["sample size", "sample", "size"])
    blank_col = find_column(columns, ["blank", "undec", "none"])
    if not pollster_col or not date_col:
        return []

    rows: list[dict[str, object]] = []
    for _, row in table.iterrows():
        pollster = str(row.get(pollster_col, "")).strip()
        date_text = str(row.get(date_col, "")).strip()
        bad_text = f"{pollster} {date_text}".lower()
        if not pollster or not date_text or any(word in bad_text for word in ["election", "results", "aggregator", "hypothetical"]):
            continue
        for candidate in CANDIDATES.get(year, []):
            col = candidate_column(columns, candidate)
            value = parse_percent(row.get(col)) if col else None
            if value is None:
                continue
            rows.append(
                {
                    "ano_eleicao": year,
                    "turno": 1,
                    "instituto": pollster,
                    "data_texto_original": date_text,
                    "amostra_texto_original": "" if sample_col is None else row.get(sample_col, ""),
                    "cenario": f"wikipedia_tabela_{index}",
                    "candidato": candidate,
                    "percentual_total": value,
                    "brancos_nulos_indecisos_texto": "" if blank_col is None else row.get(blank_col, ""),
                    "fonte": url,
                }
            )
    return rows


def collect_page(year: int, url: str) -> tuple[list[dict[str, object]], str]:
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    tables = pd.read_html(StringIO(response.text))
    rows: list[dict[str, object]] = []
    useful_tables = 0
    for index, table in enumerate(tables):
        parsed = table_to_rows(year, table, index, url)
        if parsed:
            useful_tables += 1
            rows.extend(parsed)
    return rows, f"{year}: {len(tables)} tabelas lidas, {useful_tables} aproveitadas, {len(rows)} linhas extraidas."


def main() -> None:
    all_rows: list[dict[str, object]] = []
    log_lines = ["# Coleta de pesquisas na Wikipedia", ""]
    for year, url in PAGES.items():
        try:
            rows, line = collect_page(year, url)
            all_rows.extend(rows)
            log_lines.append(f"- {line}")
        except Exception as exc:
            log_lines.append(f"- {year}: falhou ({exc}).")

    RAW.mkdir(parents=True, exist_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_rows).to_csv(OUT, index=False)
    LOG.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print(f"{len(all_rows)} linhas gravadas em {OUT}")


if __name__ == "__main__":
    main()
