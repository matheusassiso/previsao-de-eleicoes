from __future__ import annotations

import random
import warnings
from datetime import date
from pathlib import Path

import pandas as pd
from statsmodels.tsa.statespace.structural import UnobservedComponents

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PESQUISAS = PROCESSED / "pesquisas_validos.csv"
ELEICOES = RAW / "eleicoes.csv"
OUT = PROCESSED / "previsao_bayesiana_dinamica.csv"

MODEL_NAME = "bayesiano_dinamico_kalman"
SIMULATIONS = 5000


def election_date(year: int, elections: pd.DataFrame) -> date:
    row = elections[elections["ano_eleicao"] == year].iloc[0]
    return pd.to_datetime(row["data_primeiro_turno"]).date()


def daily_series(group: pd.DataFrame) -> pd.Series:
    data = group.copy()
    data["data_publicacao"] = pd.to_datetime(data["data_publicacao"])
    data["voto_valido_estimado"] = pd.to_numeric(data["voto_valido_estimado"], errors="coerce")
    data["amostra"] = pd.to_numeric(data["amostra"], errors="coerce").fillna(1).clip(lower=1)
    data = data.dropna(subset=["data_publicacao", "voto_valido_estimado"])
    if data.empty:
        return pd.Series(dtype=float)
    data["peso"] = data["amostra"] ** 0.5
    daily = data.groupby("data_publicacao").apply(
        lambda frame: (frame["voto_valido_estimado"] * frame["peso"]).sum() / frame["peso"].sum(),
        include_groups=False,
    )
    index = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    return daily.reindex(index).interpolate().ffill().bfill().clip(0, 100)


def fit_latent_forecast(series: pd.Series, target_date: date) -> tuple[float, float, float, str]:
    if series.empty:
        return 0.0, 0.0, 100.0, "sem_serie"
    last_date = series.index.max().date()
    steps = max((target_date - last_date).days, 0)
    if len(series.dropna()) < 4:
        estimate = float(series.iloc[-1])
        return estimate, max(0.0, estimate - 10.0), min(100.0, estimate + 10.0), "fallback_poucos_pontos"
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = UnobservedComponents(series, level="local level")
            fitted = model.fit(disp=False)
            forecast = fitted.get_forecast(steps=steps or 1)
        frame = forecast.summary_frame(alpha=0.05)
        row = frame.iloc[-1 if steps else 0]
        estimate = float(row["mean"])
        low = float(row["mean_ci_lower"])
        high = float(row["mean_ci_upper"])
        return min(100.0, max(0.0, estimate)), max(0.0, low), min(100.0, high), "kalman_local_level"
    except Exception:
        estimate = float(series.tail(min(len(series), 7)).mean())
        return estimate, max(0.0, estimate - 12.0), min(100.0, estimate + 12.0), "fallback_media_recente"


def rank_probabilities(candidates: list[dict[str, object]]) -> dict[str, tuple[float, float]]:
    rng = random.Random(20260912)
    counts = {str(row["candidato"]): [0, 0] for row in candidates}
    for _ in range(SIMULATIONS):
        draw = []
        for row in candidates:
            sigma = max((float(row["intervalo_alto"]) - float(row["intervalo_baixo"])) / (2 * 1.96), 0.5)
            draw.append((str(row["candidato"]), rng.gauss(float(row["voto_valido_estimado"]), sigma)))
        draw.sort(key=lambda item: item[1], reverse=True)
        counts[draw[0][0]][0] += 1
        for candidate, _ in draw[:2]:
            counts[candidate][1] += 1
    return {candidate: (lead / SIMULATIONS, top2 / SIMULATIONS) for candidate, (lead, top2) in counts.items()}


def forecast(df: pd.DataFrame, elections: pd.DataFrame, year: int = 2026, forecast_date: date | None = None) -> pd.DataFrame:
    data = df.copy()
    data["ano_eleicao"] = pd.to_numeric(data["ano_eleicao"], errors="coerce")
    data["data_publicacao"] = pd.to_datetime(data["data_publicacao"], errors="coerce")
    principal = pd.to_numeric(data.get("usar_previsao_principal", 1), errors="coerce").fillna(1)
    data = data[
        (data["ano_eleicao"] == year)
        & (data["turno"].astype(str) == "1")
        & (principal != 0)
    ].dropna(subset=["data_publicacao", "voto_valido_estimado"])
    if forecast_date is None:
        forecast_date = data["data_publicacao"].max().date()
    data = data[data["data_publicacao"].dt.date <= forecast_date]
    target_date = election_date(year, elections)
    rows = []
    for (scenario, candidate), group in data.groupby(["cenario_rotulo", "candidato"]):
        estimate, low, high, method = fit_latent_forecast(daily_series(group), target_date)
        rows.append(
            {
                "data_previsao": forecast_date.isoformat(),
                "ano_eleicao": year,
                "cenario": scenario,
                "modelo": MODEL_NAME,
                "candidato": candidate,
                "voto_valido_estimado": round(estimate, 4),
                "intervalo_baixo": round(low, 4),
                "intervalo_alto": round(high, 4),
                "probabilidade_liderar": 0.0,
                "probabilidade_ir_ao_segundo_turno": 0.0,
                "fonte_dados_ate": forecast_date.isoformat(),
                "metodo_estado_latente": method,
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    probs = []
    for _, group in out.groupby("cenario"):
        lookup = rank_probabilities(group.to_dict("records"))
        for row in group.to_dict("records"):
            lead, top2 = lookup[str(row["candidato"])]
            row["probabilidade_liderar"] = round(lead, 4)
            row["probabilidade_ir_ao_segundo_turno"] = round(top2, 4)
            probs.append(row)
    return pd.DataFrame(probs).sort_values(["cenario", "voto_valido_estimado"], ascending=[True, False])


def demo() -> None:
    series = pd.Series([40, 41, 42, 43], index=pd.date_range("2026-09-01", periods=4, freq="D"))
    estimate, low, high, method = fit_latent_forecast(series, date(2026, 9, 10))
    assert method == "kalman_local_level"
    assert low <= estimate <= high


def main() -> None:
    demo()
    result = forecast(pd.read_csv(PESQUISAS), pd.read_csv(ELEICOES))
    result.to_csv(OUT, index=False)
    print(f"{len(result)} linhas gravadas em {OUT}")


if __name__ == "__main__":
    main()
