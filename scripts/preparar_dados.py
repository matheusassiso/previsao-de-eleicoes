from __future__ import annotations

import csv
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

PESQUISAS = RAW / "pesquisas.csv"
PESQUISAS_1994_1998_FOLHA = RAW / "pesquisas_1994_1998_folha_manual.csv"
PESQUISAS_1994_2006_FOLHA = RAW / "pesquisas_1994_2006_folha_manual.csv"
PESQUISAS_2026_INICIAIS = RAW / "pesquisas_2026_iniciais.csv"
PESQUISAS_2026_RECENTES = RAW / "pesquisas_2026_agosto_setembro_manual.csv"
PESQUISAS_2002_CESOP_DATAFOLHA = RAW / "pesquisas_2002_cesop_datafolha.csv"
PESQUISAS_2002_UOL = RAW / "pesquisas_2002_uol_fernando_rodrigues.csv"
PESQUISAS_2006_WIKITEXT = RAW / "pesquisas_2006_wikitext.csv"
PESQUISAS_HISTORICAS_LIMPAS = RAW / "pesquisas_historicas_limpas.csv"
PESQUISAS_HISTORICAS_NORMALIZADAS = RAW / "pesquisas_historicas_normalizadas.csv"
RESULTADOS = RAW / "resultados_primeiro_turno.csv"
ELEICOES = RAW / "eleicoes.csv"
VARIAVEIS_CANDIDATOS = RAW / "variaveis_candidatos.csv"
CENARIOS = RAW / "cenarios.csv"
FUNDAMENTOS = RAW / "fundamentos_eleicao.csv"
SAIDA = PROCESSED / "pesquisas_validos.csv"

GROUP_FIELDS = (
    "ano_eleicao",
    "turno",
    "instituto",
    "data_publicacao",
    "cenario",
)

CANONICAL_CANDIDATES = {
    (2006, "lula"): "Lula",
    (1994, "fhc"): "Fernando Henrique Cardoso",
    (1994, "fernando henrique"): "Fernando Henrique Cardoso",
    (1994, "enéas"): "Enéas Carneiro",
    (1994, "eneas"): "Enéas Carneiro",
    (1994, "amin"): "Esperidião Amin",
    (1998, "fhc"): "Fernando Henrique Cardoso",
    (1998, "fernando henrique"): "Fernando Henrique Cardoso",
    (1998, "enéas"): "Enéas Carneiro",
    (1998, "eneas"): "Enéas Carneiro",
    (2002, "garotinho"): "Anthony Garotinho",
    (2002, "anthony garotinho"): "Anthony Garotinho",
    (2006, "geraldo alckmin"): "Geraldo Alckmin",
    (2006, "alckmin"): "Geraldo Alckmin",
    (2006, "heloísa helena"): "Heloísa Helena",
    (2006, "heloisa helena"): "Heloísa Helena",
    (2006, "helo�sa helena"): "Heloísa Helena",
    (2006, "cristovam buarque"): "Cristovam Buarque",
    (2006, "ana maria rangel"): "Ana Maria Rangel",
    (2010, "dilma"): "Dilma Rousseff",
    (2010, "serra"): "José Serra",
    (2010, "marina"): "Marina Silva",
    (2010, "plínio"): "Plínio de Arruda Sampaio",
    (2010, "plinio"): "Plínio de Arruda Sampaio",
    (2014, "dilma"): "Dilma Rousseff",
    (2014, "rousseff"): "Dilma Rousseff",
    (2014, "aécio"): "Aécio Neves",
    (2014, "aecio"): "Aécio Neves",
    (2014, "neves"): "Aécio Neves",
    (2014, "marina"): "Marina Silva",
    (2014, "luciana genro"): "Luciana Genro",
    (2014, "pastor everaldo"): "Pastor Everaldo",
    (2014, "eduardo jorge"): "Eduardo Jorge",
    (2018, "bolsonaro"): "Jair Bolsonaro",
    (2018, "haddad"): "Fernando Haddad",
    (2018, "ciro"): "Ciro Gomes",
    (2018, "gomes"): "Ciro Gomes",
    (2018, "alckmin"): "Geraldo Alckmin",
    (2018, "amoêdo"): "João Amoêdo",
    (2018, "amoedo"): "João Amoêdo",
    (2018, "marina"): "Marina Silva",
    (2022, "bolsonaro"): "Jair Bolsonaro",
    (2022, "lula"): "Lula",
    (2022, "gomes"): "Ciro Gomes",
    (2022, "ciro"): "Ciro Gomes",
    (2022, "tebet"): "Simone Tebet",
}


def parse_float(value: str) -> float:
    return float((value or "0").replace(",", "."))


def parse_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def canonical_candidate(year: str, candidate: str) -> str:
    key = (int(year), candidate.strip().lower())
    return CANONICAL_CANDIDATES.get(key, candidate.strip())


def clean_institute(institute: str) -> str:
    return re.sub(r"\[\d+\]", "", institute or "").strip()


def poll_key(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row[field] for field in GROUP_FIELDS)


def load_results(path: Path) -> dict[tuple[str, str], float]:
    with path.open(newline="", encoding="utf-8") as file:
        return {
            (row["ano_eleicao"], row["candidato"].strip().lower()): parse_float(row["percentual_validos"])
            for row in csv.DictReader(file)
            if row.get("ano_eleicao") and row.get("candidato") and row.get("percentual_validos")
        }


def load_election_dates(path: Path) -> dict[str, object]:
    with path.open(newline="", encoding="utf-8") as file:
        return {
            row["ano_eleicao"]: parse_date(row["data_primeiro_turno"])
            for row in csv.DictReader(file)
            if row.get("ano_eleicao") and row.get("data_primeiro_turno")
        }


def load_candidate_variables(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as file:
        return {
            (row["ano_eleicao"], row["candidato"].strip().lower()): row
            for row in csv.DictReader(file)
            if row.get("ano_eleicao") and row.get("candidato")
        }


def load_scenarios(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as file:
        return {
            (row["ano_eleicao"], row["cenario"]): row
            for row in csv.DictReader(file)
            if row.get("ano_eleicao") and row.get("cenario")
        }


def load_fundamentals(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as file:
        return {row["ano_eleicao"]: row for row in csv.DictReader(file) if row.get("ano_eleicao")}


def read_poll_rows(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        if not path.exists():
            continue
        with path.open(newline="", encoding="utf-8") as file:
            rows.extend(row for row in csv.DictReader(file) if row.get("candidato"))
    return rows


def prepare_rows(poll_paths: list[Path], results_path: Path) -> list[dict[str, str]]:
    results = load_results(results_path)
    election_dates = load_election_dates(ELEICOES)
    candidate_variables = load_candidate_variables(VARIAVEIS_CANDIDATOS)
    scenarios = load_scenarios(CENARIOS)
    fundamentals = load_fundamentals(FUNDAMENTOS)
    rows = read_poll_rows(poll_paths)
    for row in rows:
        row["candidato"] = canonical_candidate(row["ano_eleicao"], row["candidato"])
        row["instituto"] = clean_institute(row.get("instituto", ""))
    rows = [
        row
        for row in rows
        if not election_dates.get(row["ano_eleicao"])
        or parse_date(row["data_fim_campo"]) <= election_dates[row["ano_eleicao"]]
    ]

    for row in rows:
        base_valida = 100 - parse_float(row["brancos_nulos"]) - parse_float(row["indecisos"])
        row["_voto_valido_bruto"] = parse_float(row["percentual_total"]) / base_valida * 100 if base_valida > 0 else 0

    ordered = sorted(rows, key=lambda row: (row["ano_eleicao"], row["data_publicacao"], row["instituto"], row["cenario"]))
    campaign_order: dict[str, int] = defaultdict(int)
    institute_order: dict[tuple[str, str, str], int] = defaultdict(int)
    seen_polls: set[tuple[str, ...]] = set()
    for row in ordered:
        key = poll_key(row)
        if key in seen_polls:
            continue
        seen_polls.add(key)
        year = row["ano_eleicao"]
        campaign_order[year] += 1
        institute_key = (year, row["instituto"], row["cenario"])
        institute_order[institute_key] += 1
        for candidate_row in [candidate for candidate in rows if poll_key(candidate) == key]:
            candidate_row["_ordem_pesquisa_campanha"] = campaign_order[year]
            candidate_row["_ordem_pesquisa_instituto_cenario"] = institute_order[institute_key]

    groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[poll_key(row)].append(row)

    prepared: list[dict[str, str]] = []
    for group_rows in groups.values():
        for row in group_rows:
            candidato_key = (row["ano_eleicao"], row["candidato"].strip().lower())
            estimado = float(row["_voto_valido_bruto"])
            real = results.get(candidato_key)
            out = {key: value for key, value in row.items() if not key.startswith("_")}
            variables = candidate_variables.get(candidato_key, {})
            scenario = scenarios.get((row["ano_eleicao"], row["cenario"]), {})
            foundation = fundamentals.get(row["ano_eleicao"], {})
            out["incumbente"] = variables.get("incumbente", "")
            out["sucessor_governo"] = variables.get("sucessor_governo", "")
            out["partido_governo"] = variables.get("partido_governo", "")
            out["reeleicao_permitida"] = variables.get("reeleicao_permitida", "")
            out["ex_presidente"] = variables.get("ex_presidente", "")
            out["pib_crescimento"] = foundation.get("pib_crescimento", "")
            out["inflacao"] = foundation.get("inflacao", "")
            out["desemprego"] = foundation.get("desemprego", "")
            out["fundamentos_ano_referencia"] = foundation.get("fundamentos_ano_referencia", "")
            out["fundamentos_defasagem_max"] = foundation.get("fundamentos_defasagem_max", "")
            out["cenario_rotulo"] = scenario.get("rotulo", row["cenario"])
            out["cenario_prioridade"] = scenario.get("prioridade", "")
            out["usar_previsao_principal"] = scenario.get("usar_previsao_principal", "")
            election_date = election_dates.get(row["ano_eleicao"])
            if election_date:
                out["dias_campo_ate_eleicao"] = str((election_date - parse_date(row["data_fim_campo"])).days)
                out["dias_publicacao_ate_eleicao"] = str((election_date - parse_date(row["data_publicacao"])).days)
            else:
                out["dias_campo_ate_eleicao"] = ""
                out["dias_publicacao_ate_eleicao"] = ""
            out["ordem_pesquisa_instituto_cenario"] = str(row.get("_ordem_pesquisa_instituto_cenario", ""))
            out["ordem_pesquisa_campanha"] = str(row.get("_ordem_pesquisa_campanha", ""))
            out["voto_valido_estimado"] = f"{estimado:.4f}"
            out["resultado_real_validos"] = "" if real is None else f"{real:.4f}"
            out["erro"] = "" if real is None else f"{real - estimado:.4f}"
            prepared.append(out)

    return prepared


def write_rows(rows: list[dict[str, str]], path: Path) -> None:
    fields = list(csv.DictReader(PESQUISAS.open(newline="", encoding="utf-8")).fieldnames or [])
    for row in rows:
        for field in row:
            if field not in fields and not field.startswith("_"):
                fields.append(field)
    for field in [
        "incumbente",
        "sucessor_governo",
        "partido_governo",
        "reeleicao_permitida",
        "ex_presidente",
        "pib_crescimento",
        "inflacao",
        "desemprego",
        "fundamentos_ano_referencia",
        "fundamentos_defasagem_max",
        "cenario_rotulo",
        "cenario_prioridade",
        "usar_previsao_principal",
        "dias_campo_ate_eleicao",
        "dias_publicacao_ate_eleicao",
        "ordem_pesquisa_instituto_cenario",
        "ordem_pesquisa_campanha",
    ]:
        if field not in fields:
            fields.append(field)
    for field in ["voto_valido_estimado", "resultado_real_validos", "erro"]:
        if field not in fields:
            fields.append(field)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def demo() -> None:
    rows = [
        {"ano_eleicao": "2022", "turno": "1", "instituto": "X", "data_inicio_campo": "2022-09-01", "data_fim_campo": "2022-09-02", "data_publicacao": "2022-09-03", "amostra": "1000", "cenario": "A", "candidato": "A", "percentual_total": "40", "brancos_nulos": "10", "indecisos": "10", "fonte": "demo"},
        {"ano_eleicao": "2022", "turno": "1", "instituto": "X", "data_inicio_campo": "2022-09-01", "data_fim_campo": "2022-09-02", "data_publicacao": "2022-09-03", "amostra": "1000", "cenario": "A", "candidato": "B", "percentual_total": "40", "brancos_nulos": "10", "indecisos": "10", "fonte": "demo"},
    ]
    for row in rows:
        base_valida = 100 - parse_float(row["brancos_nulos"]) - parse_float(row["indecisos"])
        row["_voto_valido_bruto"] = parse_float(row["percentual_total"]) / base_valida * 100
    total = sum(float(row["_voto_valido_bruto"]) for row in rows)
    assert round(float(rows[0]["_voto_valido_bruto"]), 1) == 50.0
    assert (parse_date("2022-10-02") - parse_date("2022-09-02")).days == 30
    assert clean_institute("Atlas[20]") == "Atlas"


def main() -> None:
    poll_paths = [PESQUISAS]
    if PESQUISAS_HISTORICAS_LIMPAS.exists():
        poll_paths.append(PESQUISAS_HISTORICAS_LIMPAS)
    elif PESQUISAS_HISTORICAS_NORMALIZADAS.exists():
        poll_paths.append(PESQUISAS_HISTORICAS_NORMALIZADAS)
    else:
        poll_paths.append(PESQUISAS_2026_INICIAIS)
    if PESQUISAS_2006_WIKITEXT.exists():
        poll_paths.append(PESQUISAS_2006_WIKITEXT)
    if PESQUISAS_2002_CESOP_DATAFOLHA.exists():
        poll_paths.append(PESQUISAS_2002_CESOP_DATAFOLHA)
    if PESQUISAS_2002_UOL.exists():
        poll_paths.append(PESQUISAS_2002_UOL)
    if PESQUISAS_1994_1998_FOLHA.exists():
        poll_paths.append(PESQUISAS_1994_1998_FOLHA)
    if PESQUISAS_1994_2006_FOLHA.exists():
        poll_paths.append(PESQUISAS_1994_2006_FOLHA)
    if PESQUISAS_2026_RECENTES.exists():
        poll_paths.append(PESQUISAS_2026_RECENTES)
    rows = prepare_rows(poll_paths, RESULTADOS)
    write_rows(rows, SAIDA)
    print(f"{len(rows)} linhas gravadas em {SAIDA}")


if __name__ == "__main__":
    demo()
    main()
