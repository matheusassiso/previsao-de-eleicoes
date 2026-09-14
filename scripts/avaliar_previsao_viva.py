from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error

from ajustes_literatura import adjusted_vote, house_effect_lookup, house_effect_stats, house_effect_vote, institute_stats, stats_lookup, temporal_projection
from bayesiano_dinamico import MODEL_NAME as BAYESIAN_MODEL, daily_series, fit_latent_forecast

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
PESQUISAS = PROCESSED / "pesquisas_validos.csv"
OUT = PROCESSED / "backtest_previsao_viva.csv"

WINDOWS = [180, 120, 90, 60, 30, 15, 7]


def weighted_average(group: pd.DataFrame, value_col: str = "voto_valido_estimado") -> float:
    weights = group["amostra"].clip(lower=1) ** 0.5
    return float((group[value_col] * weights).sum() / weights.sum())


def simulate_live_forecast(df: pd.DataFrame, windows: list[int] = WINDOWS) -> pd.DataFrame:
    rows = []
    historic = df.dropna(subset=["resultado_real_validos"]).copy()
    for year in sorted(historic["ano_eleicao"].unique()):
        year_df = historic[historic["ano_eleicao"] == year]
        train = historic[historic["ano_eleicao"] < year]
        lookup = stats_lookup(institute_stats(train)) if not train.empty else {}
        house_lookup = house_effect_lookup(house_effect_stats(train)) if not train.empty else {}
        for window in windows:
            available = year_df[year_df["dias_publicacao_ate_eleicao"] >= window]
            if available.empty:
                continue
            available = available.copy()
            available["baseline_ajustado"] = available.apply(lambda row: adjusted_vote(row, lookup), axis=1)
            available["baseline_efeito_casa"] = available.apply(lambda row: house_effect_vote(row, house_lookup, lookup), axis=1)
            forecasts = []
            for model, value_col in [("baseline_pesquisa", "voto_valido_estimado"), ("baseline_ajustado", "baseline_ajustado"), ("baseline_efeito_casa", "baseline_efeito_casa")]:
                forecast = (
                    available.groupby(["cenario", "candidato"])
                    .apply(lambda group: weighted_average(group, value_col), include_groups=False)
                    .reset_index(name="previsto")
                )
                forecast["modelo"] = model
                forecasts.append(forecast)
            election_date = (pd.to_datetime(available["data_publicacao"]) + pd.to_timedelta(available["dias_publicacao_ate_eleicao"], unit="D")).max().date()
            temporal = (
                available.groupby(["cenario", "candidato"])
                .apply(lambda group: temporal_projection(group, election_date), include_groups=False)
                .reset_index(name="previsto")
            )
            temporal["modelo"] = "baseline_temporal"
            forecasts.append(temporal)
            bayesian = (
                available.groupby(["cenario", "candidato"])
                .apply(lambda group: fit_latent_forecast(daily_series(group), election_date)[0], include_groups=False)
                .reset_index(name="previsto")
            )
            bayesian["modelo"] = BAYESIAN_MODEL
            forecasts.append(bayesian)
            forecast = pd.concat(forecasts, ignore_index=True)
            real = available[["cenario", "candidato", "resultado_real_validos"]].drop_duplicates()
            scored = forecast.merge(real, on=["cenario", "candidato"], how="inner")
            if scored.empty:
                continue
            for model, group in scored.groupby("modelo"):
                rows.append(
                    {
                        "ano_teste": int(year),
                        "dias_antes_eleicao": window,
                        "modelo": model,
                        "linhas_avaliadas": len(group),
                        "mae": mean_absolute_error(group["resultado_real_validos"], group["previsto"]),
                    }
                )
    return pd.DataFrame(rows)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(PESQUISAS)
    for column in ["ano_eleicao", "dias_publicacao_ate_eleicao", "amostra", "voto_valido_estimado", "resultado_real_validos"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def main() -> None:
    result = simulate_live_forecast(load_data())
    result.to_csv(OUT, index=False)
    print(f"{len(result)} linhas gravadas em {OUT}")
    if not result.empty:
        print(result.groupby("dias_antes_eleicao")["mae"].mean().to_string())


if __name__ == "__main__":
    main()
