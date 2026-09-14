from __future__ import annotations

import re
import urllib.request
from io import StringIO
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = RAW / "pesquisas_2002_uol_fernando_rodrigues.csv"
URL = "https://www1.uol.com.br/fernandorodrigues/arquivos/pesquisas/eleicoes2002/pres.shl"

MONTHS = {"jan": "01", "fev": "02", "mar": "03", "abr": "04", "mai": "05", "jun": "06", "jul": "07", "ago": "08", "set": "09", "out": "10"}
CANDIDATES = {
    "Lula (PT)": "Lula",
    "Jos� Serra (PSDB)": "José Serra",
    "Anthony Garotinho (PSB)": "Anthony Garotinho",
    "Ciro Gomes (PPS)": "Ciro Gomes",
}


def parse_number(value: object) -> float | None:
    text = str(value).strip().replace(",", ".")
    if text in {"", "-", "nan", "n.d.", "NaN"}:
        return None
    match = re.search(r"\d+(?:\.\d+)?", text)
    return float(match.group()) if match else None


def parse_poll_dates(value: str) -> tuple[str, str]:
    raw = str(value).lower().replace("agol", "ago").replace("01/", "1/")
    if " a " in raw:
        start, end = [part.replace(" ", "") for part in raw.split(" a ", 1)]
        end_date = parse_single_date(end)
        if start.count("/") == 1:
            day, month = start.split("/")
            year = end.split("/")[-1]
            start = f"{day}/{month}/{year}"
        return parse_single_date(start), end_date
    text = raw.replace(" ", "")
    if "-" in text:
        left, right = text.split("-", 1)
        if "/" not in left:
            day, rest = right.split("/", 1)
            month, year = rest.split("/", 1)
            return f"20{year}-{MONTHS[month[:3]]}-{int(left):02d}", f"20{year}-{MONTHS[month[:3]]}-{int(day):02d}"
        return parse_single_date(left), parse_single_date(right)
    parsed = parse_single_date(text)
    return parsed, parsed


def parse_single_date(value: str) -> str:
    day, month, year = value.split("/")
    return f"20{year}-{MONTHS[month[:3]]}-{int(day):02d}"


def load_table() -> pd.DataFrame:
    html = urllib.request.urlopen(URL, timeout=30).read().decode("latin-1")
    raw = pd.read_html(StringIO(html), decimal=",", thousands=".")[2]
    raw.columns = raw.iloc[2]
    return raw.iloc[3:].reset_index(drop=True)


def build_rows(table: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for i, poll in table.iterrows():
        blank_null = parse_number(poll.get("Branco, nulo ou nenhum"))
        undecided = parse_number(poll.get("N�o sabe"))
        no_candidate = parse_number(poll.get("Sem cand."))
        if blank_null is None and undecided is None:
            if no_candidate is None:
                continue
            blank_null, undecided = 0.0, no_candidate
        else:
            blank_null = blank_null or 0.0
            undecided = undecided or 0.0
        start, end = parse_poll_dates(str(poll["data da pesquisa"]))
        institute = str(poll["Instituto"]).replace(" (votos v�lidos)", "").strip()
        scenario = f"uol_fernando_rodrigues_2002_{i:03d}"
        for column, candidate in CANDIDATES.items():
            value = parse_number(poll.get(column))
            if value is None:
                continue
            rows.append(
                {
                    "ano_eleicao": 2002,
                    "turno": 1,
                    "instituto": institute,
                    "data_inicio_campo": start,
                    "data_fim_campo": end,
                    "data_publicacao": end,
                    "amostra": 1000,
                    "cenario": scenario,
                    "candidato": candidate,
                    "percentual_total": value,
                    "brancos_nulos": blank_null,
                    "indecisos": undecided,
                    "fonte": URL,
                    "amostra_imputada": 1,
                    "qualidade_fonte": "secundaria_uol_fernando_rodrigues",
                    "cenario_tipo": "estimulado_primeiro_turno",
                }
            )
    return pd.DataFrame(rows)


def demo() -> None:
    assert parse_poll_dates("4-5/out/02") == ("2002-10-04", "2002-10-05")
    assert parse_poll_dates("31/jul a 1/ago/02") == ("2002-07-31", "2002-08-01")
    assert parse_number("40,6") == 40.6


def main() -> None:
    demo()
    rows = build_rows(load_table())
    rows.to_csv(OUT, index=False)
    print(f"{len(rows)} linhas gravadas em {OUT}")


if __name__ == "__main__":
    main()
