from __future__ import annotations

from datetime import date
from pathlib import Path
import re

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
IN = RAW / "pesquisas_historicas_wikipedia.csv"
OUT = RAW / "pesquisas_historicas_normalizadas.csv"

MONTHS = {
    "jan": 1,
    "january": 1,
    "fev": 2,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "abr": 4,
    "apr": 4,
    "april": 4,
    "mai": 5,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "ago": 8,
    "aug": 8,
    "august": 8,
    "set": 9,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "out": 10,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dez": 12,
    "dec": 12,
    "december": 12,
}


def parse_number(value) -> float:
    text = str(value).replace(",", "").replace("%", "").strip()
    match = re.search(r"\d+(?:\.\d+)?", text)
    return float(match.group(0)) if match else 0.0


def month_token(token: str) -> int | None:
    return MONTHS.get(token.lower()[:3]) or MONTHS.get(token.lower())


def parse_date_range(text: str, default_year: int) -> tuple[str, str] | None:
    cleaned = str(text).replace("�", " ").replace("–", " ").replace("—", " ").replace("-", " ")
    tokens = re.findall(r"\d{1,4}|[A-Za-z]+", cleaned)
    years = [int(token) for token in tokens if token.isdigit() and len(token) == 4]
    has_explicit_year = bool(years)
    year = years[-1] if has_explicit_year else default_year
    tokens = [token for token in tokens if not (token.isdigit() and len(token) == 4)]
    month_positions = [(i, month_token(token)) for i, token in enumerate(tokens) if month_token(token)]
    if not month_positions:
        return None

    if len(month_positions) == 1:
        month_index, month = month_positions[0]
        days = [int(token) for token in tokens[:month_index] if token.isdigit()]
        if not days:
            return None
        start_day, end_day = days[0], days[-1]
        start_month = end_month = month
    else:
        first_month_index, start_month = month_positions[0]
        second_month_index, end_month = month_positions[-1]
        start_candidates = [int(token) for token in tokens[:first_month_index] if token.isdigit()]
        end_candidates = [int(token) for token in tokens[first_month_index + 1 : second_month_index] if token.isdigit()]
        if not start_candidates or not end_candidates:
            return None
        start_day, end_day = start_candidates[-1], end_candidates[-1]

    try:
        start_date = date(year, start_month, start_day)
        end_date = date(year, end_month, end_day)
        if not has_explicit_year and default_year == 2026 and end_date > date.today():
            start_date = date(year - 1, start_month, start_day)
            end_date = date(year - 1, end_month, end_day)
        return start_date.isoformat(), end_date.isoformat()
    except ValueError:
        return None


def normalize() -> pd.DataFrame:
    raw = pd.read_csv(IN)
    rows = []
    for _, row in raw.iterrows():
        year = int(row["ano_eleicao"])
        parsed = parse_date_range(row["data_texto_original"], year)
        if not parsed:
            continue
        start, end = parsed
        rows.append(
            {
                "ano_eleicao": year,
                "turno": 1,
                "instituto": str(row["instituto"]).replace(" Archived", "").strip(),
                "data_inicio_campo": start,
                "data_fim_campo": end,
                "data_publicacao": end,
                "amostra": int(parse_number(row.get("amostra_texto_original", 0))),
                "cenario": row["cenario"],
                "candidato": row["candidato"],
                "percentual_total": row["percentual_total"],
                "brancos_nulos": 0,
                "indecisos": parse_number(row.get("brancos_nulos_indecisos_texto", 0)),
                "fonte": row["fonte"],
            }
        )
    return pd.DataFrame(rows)


def demo() -> None:
    assert parse_date_range("30 Sep - 1 Oct", 2022) == ("2022-09-30", "2022-10-01")
    assert parse_date_range("2-5 October 2018", 2018) == ("2018-10-02", "2018-10-05")
    assert parse_date_range("8-10 Sep 2026", 2026) == ("2026-09-08", "2026-09-10")


def main() -> None:
    demo()
    df = normalize()
    df.to_csv(OUT, index=False)
    print(f"{len(df)} linhas gravadas em {OUT}")


if __name__ == "__main__":
    main()
