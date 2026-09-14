from __future__ import annotations

import csv
import argparse
import random
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from ajustes_literatura import adjusted_vote, house_effect_lookup, house_effect_stats, house_effect_vote, institute_stats, poll_weight, stats_lookup, temporal_projection

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
PESQUISAS_VALIDOS = PROCESSED / "pesquisas_validos.csv"
PREVISOES = PROCESSED / "previsoes.csv"
BACKTEST = PROCESSED / "backtest_modelos.csv"
DEFAULT_INTERVAL = 6.0
SIMULATIONS = 5000

def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_float(value: str) -> float:
    return float((value or "0").replace(",", "."))


def load_calibration(path: Path = BACKTEST) -> dict[str, float]:
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    if df.empty or "modelo" not in df or "mae" not in df:
        return {}
    return df.groupby("modelo")["mae"].mean().to_dict()


def interval_width(model: str, calibration: dict[str, float]) -> float:
    mae = float(calibration.get(model, DEFAULT_INTERVAL / 1.96))
    return round(max(4.0, min(18.0, 1.96 * mae)), 4)


def rank_probabilities(candidates: list[tuple[str, float]], width: float) -> dict[str, tuple[float, float]]:
    sigma = max(width / 1.96, 0.1)
    counts = {candidate: [0, 0] for candidate, _ in candidates}
    rng = random.Random(20260912)
    for _ in range(SIMULATIONS):
        draw = sorted(((candidate, rng.gauss(value, sigma)) for candidate, value in candidates), key=lambda item: item[1], reverse=True)
        counts[draw[0][0]][0] += 1
        for candidate, _ in draw[:2]:
            counts[candidate][1] += 1
    return {candidate: (lead / SIMULATIONS, top2 / SIMULATIONS) for candidate, (lead, top2) in counts.items()}


def forecast(rows: list[dict[str, str]], forecast_date: date, year: str = "2026", calibration: dict[str, float] | None = None) -> list[dict[str, str]]:
    eligible = [
        row
        for row in rows
        if row["ano_eleicao"] == year
        and row["turno"] == "1"
        and row.get("voto_valido_estimado")
        and row.get("usar_previsao_principal", "1") != "0"
        and parse_date(row["data_publicacao"]) <= forecast_date
    ]

    historic = pd.DataFrame([row for row in rows if row.get("resultado_real_validos")])
    if not historic.empty:
        for column in ["voto_valido_estimado", "resultado_real_validos"]:
            historic[column] = pd.to_numeric(historic[column], errors="coerce")
    lookup = stats_lookup(institute_stats(historic)) if not historic.empty else {}
    house_lookup = house_effect_lookup(house_effect_stats(historic)) if not historic.empty else {}

    totals: dict[tuple[str, str, str], float] = defaultdict(float)
    calibration = calibration or {}
    weights: dict[tuple[str, str, str], float] = defaultdict(float)
    latest_source = ""
    for row in eligible:
        base_key = (row.get("cenario_rotulo") or row["cenario"], row["candidato"])
        pure_weight = poll_weight(row, forecast_date)
        adjusted_weight = poll_weight(row, forecast_date, lookup)
        totals[(*base_key, "baseline_pesquisa")] += parse_float(row["voto_valido_estimado"]) * pure_weight
        totals[(*base_key, "baseline_ajustado")] += adjusted_vote(row, lookup) * adjusted_weight
        totals[(*base_key, "baseline_efeito_casa")] += house_effect_vote(row, house_lookup, lookup) * adjusted_weight
        weights[(*base_key, "baseline_pesquisa")] += pure_weight
        weights[(*base_key, "baseline_ajustado")] += adjusted_weight
        weights[(*base_key, "baseline_efeito_casa")] += adjusted_weight
        latest_source = max(latest_source, row["data_publicacao"])

    by_scenario: dict[tuple[str, str], list[tuple[str, float]]] = defaultdict(list)
    for (scenario, candidate, model), total in totals.items():
        by_scenario[(scenario, model)].append((candidate, total / weights[(scenario, candidate, model)]))
    if eligible:
        frame = pd.DataFrame(eligible)
        for column in ["voto_valido_estimado", "amostra"]:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        scenario_labels = frame["cenario_rotulo"].fillna(frame["cenario"]) if "cenario_rotulo" in frame else frame["cenario"]
        for (scenario, candidate), group in frame.groupby([scenario_labels, "candidato"]):
            by_scenario[(scenario, "baseline_temporal")].append((candidate, temporal_projection(group, f"{year}-10-04")))

    output: list[dict[str, str]] = []
    for (scenario, model), candidates in by_scenario.items():
        ordered = sorted(candidates, key=lambda item: item[1], reverse=True)
        width = interval_width(model, calibration)
        probabilities = rank_probabilities(ordered, width)
        for candidate, estimate in ordered:
            lead_prob, top2_prob = probabilities[candidate]
            output.append(
                {
                    "data_previsao": forecast_date.isoformat(),
                    "ano_eleicao": year,
                    "cenario": scenario,
                    "modelo": model,
                    "candidato": candidate,
                    "voto_valido_estimado": f"{estimate:.4f}",
                    "intervalo_baixo": f"{max(0, estimate - width):.4f}",
                    "intervalo_alto": f"{min(100, estimate + width):.4f}",
                    "probabilidade_liderar": f"{lead_prob:.4f}",
                    "probabilidade_ir_ao_segundo_turno": f"{top2_prob:.4f}",
                    "fonte_dados_ate": latest_source,
                }
            )
    return output


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def default_forecast_date(rows: list[dict[str, str]]) -> date:
    dates = [parse_date(row["data_publicacao"]) for row in rows if row.get("data_publicacao")]
    return max(dates) if dates else date.today()


def write_rows(rows: list[dict[str, str]], path: Path) -> None:
    fields = [
        "data_previsao",
        "ano_eleicao",
        "cenario",
        "modelo",
        "candidato",
        "voto_valido_estimado",
        "intervalo_baixo",
        "intervalo_alto",
        "probabilidade_liderar",
        "probabilidade_ir_ao_segundo_turno",
        "fonte_dados_ate",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def demo() -> None:
    rows = [
        {"ano_eleicao": "2026", "turno": "1", "data_publicacao": "2026-09-01", "amostra": "1000", "cenario": "A", "candidato": "A", "voto_valido_estimado": "60"},
        {"ano_eleicao": "2026", "turno": "1", "data_publicacao": "2026-09-01", "amostra": "1000", "cenario": "A", "candidato": "B", "voto_valido_estimado": "40"},
    ]
    result = forecast(rows, date(2026, 9, 2))
    assert result[0]["candidato"] == "A"
    assert float(result[0]["probabilidade_liderar"]) > 0.9


def main() -> None:
    demo()
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-previsao", help="Data da previsao em AAAA-MM-DD. Padrao: ultima pesquisa disponivel.")
    args = parser.parse_args()
    loaded = load_rows(PESQUISAS_VALIDOS)
    forecast_date = parse_date(args.data_previsao) if args.data_previsao else default_forecast_date(loaded)
    rows = forecast(loaded, forecast_date, calibration=load_calibration())
    write_rows(rows, PREVISOES)
    print(f"{len(rows)} linhas gravadas em {PREVISOES}")


if __name__ == "__main__":
    main()
