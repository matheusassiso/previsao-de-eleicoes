from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DOCS = ROOT / "docs"
OUT = RAW / "pesquisas_2006_wikitext.csv"
REPORT = DOCS / "coleta-2006-wikitext.md"
URL = "https://pt.wikipedia.org/w/index.php?title=Elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2006&action=raw"

FIELDS = [
    "ano_eleicao",
    "turno",
    "instituto",
    "data_inicio_campo",
    "data_fim_campo",
    "data_publicacao",
    "amostra",
    "cenario",
    "candidato",
    "percentual_total",
    "brancos_nulos",
    "indecisos",
    "fonte",
]


def fetch_text(url: str = URL) -> str:
    request = Request(url, headers={"User-Agent": "Codex election forecast research"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def fix_label(label: str) -> str:
    return " ".join(label.replace("Helo�sa", "Heloísa").split())


def parse_date(value: str) -> str:
    return datetime.strptime(value, "%d/%m/%y").date().isoformat()


def first_round_section(text: str) -> str:
    polls = text.find("== Pesquisas ==")
    start = text.find("; Primeiro turno", polls)
    end = text.find("\n==", start + 1)
    return text[start:end if end != -1 else len(text)]


def parse_block(block: str) -> list[dict[str, str]]:
    date_match = re.search(r'text:"Pesquisa\s+(\d{2}/\d{2}/\d{2})"', block)
    source_match = re.search(r'text:"Fonte:\s*([^"]+)"', block)
    sample_match = re.search(r"Total de entrevistados:\s*([\d.]+)", block)
    if not (date_match and source_match and sample_match):
        return []

    poll_date = parse_date(date_match.group(1))
    sample = sample_match.group(1).replace(".", "")
    source = fix_label(source_match.group(1))
    institute = source.replace("Estado/", "")
    labels = re.findall(r'text:"([^"]+?)\s*\(([\d,.]+)%\)"', block)
    brancos_nulos = "0"
    indecisos = "0"
    candidate_rows = []
    for raw_label, raw_pct in labels:
        label = fix_label(raw_label)
        pct = raw_pct.replace(",", ".")
        lower = label.lower()
        if "brancos" in lower or "nulos" in lower:
            if "indecisos" in lower:
                indecisos = pct
            else:
                brancos_nulos = pct
        elif "indecisos" in lower:
            indecisos = pct
        else:
            candidate_rows.append((label, pct))

    return [
        {
            "ano_eleicao": "2006",
            "turno": "1",
            "instituto": institute,
            "data_inicio_campo": poll_date,
            "data_fim_campo": poll_date,
            "data_publicacao": poll_date,
            "amostra": sample,
            "cenario": "wikipedia_2006_primeiro_turno",
            "candidato": candidate,
            "percentual_total": pct,
            "brancos_nulos": brancos_nulos,
            "indecisos": indecisos,
            "fonte": "Wikipedia pt 2006 wikitext: pesquisa de primeiro turno",
        }
        for candidate, pct in candidate_rows
    ]


def parse_first_round(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for block in first_round_section(text).split("<timeline>")[1:]:
        rows.extend(parse_block(block))
    return rows


def write_rows(rows: list[dict[str, str]]) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    REPORT.write_text(
        "\n".join(
            [
                "# Coleta de pesquisas de 2006 em wikitexto",
                "",
                f"- Fonte: {URL}",
                f"- Linhas extraidas: {len(rows)}.",
                "- Escopo: somente graficos marcados como primeiro turno na pagina.",
                "- Observacao: quando a fonte junta brancos/nulos e indecisos, o valor entra como abatimento total da base valida.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def demo() -> None:
    sample = '== Pesquisas ==\n; Primeiro turno\n<timeline>text:"Lula (49%)" text:"Votos brancos e nulos e Indecisos (9%)" text:"Pesquisa 30/09/06" text:"Fonte: Datafolha"</timeline>\n* Total de entrevistados: 7.528\n== Fim =='
    assert parse_first_round(sample)[0]["amostra"] == "7528"


def main() -> None:
    demo()
    rows = parse_first_round(fetch_text())
    write_rows(rows)
    print(f"{len(rows)} linhas gravadas em {OUT}")
    print(f"auditoria gravada em {REPORT}")


if __name__ == "__main__":
    main()
