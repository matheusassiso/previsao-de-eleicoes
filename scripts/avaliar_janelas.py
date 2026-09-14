from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error

from ajustes_literatura import adjusted_vote, house_effect_lookup, house_effect_stats, house_effect_vote, institute_stats, stats_lookup, temporal_projection
from bayesiano_dinamico import MODEL_NAME as BAYESIAN_MODEL, daily_series, fit_latent_forecast

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
PESQUISAS = PROCESSED / "pesquisas_validos.csv"
OUT = PROCESSED / "backtest_janelas.csv"

WINDOWS = [180, 120, 90, 60, 30, 15, 7]


def weighted_average(group: pd.DataFrame, value_col: str = "voto_valido_estimado") -> float:
    weights = group["amostra"].clip(lower=1) ** 0.5
    return float((group[value_col] * weights).sum() / weights.sum())


def evaluate(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    historic = df.dropna(subset=["resultado_real_validos"]).copy()
    for year in sorted(historic["ano_eleicao"].unique()):
        year_df = historic[historic["ano_eleicao"] == year]
        train = historic[historic["ano_eleicao"] < year]
        lookup = stats_lookup(institute_stats(train)) if not train.empty else {}
        house_lookup = house_effect_lookup(house_effect_stats(train)) if not train.empty else {}
        for window in WINDOWS:
            available = year_df[year_df["dias_campo_ate_eleicao"] >= window]
            if available.empty:
                continue
            latest = available.groupby(["cenario", "candidato"])["data_fim_campo"].transform("max")
            latest_rows = available[available["data_fim_campo"] == latest].copy()
            latest_rows["baseline_ajustado"] = latest_rows.apply(lambda row: adjusted_vote(row, lookup), axis=1)
            latest_rows["baseline_efeito_casa"] = latest_rows.apply(lambda row: house_effect_vote(row, house_lookup, lookup), axis=1)
            preds = []
            for model, value_col in [("baseline_pesquisa", "voto_valido_estimado"), ("baseline_ajustado", "baseline_ajustado"), ("baseline_efeito_casa", "baseline_efeito_casa")]:
                pred = (
                    latest_rows.groupby(["cenario", "candidato"])
                    .apply(lambda group: weighted_average(group, value_col), include_groups=False)
                    .reset_index(name="previsto")
                )
                pred["modelo"] = model
                preds.append(pred)
            election_date = (pd.to_datetime(latest_rows["data_fim_campo"]) + pd.to_timedelta(latest_rows["dias_campo_ate_eleicao"], unit="D")).max().date()
            temporal = (
                available.groupby(["cenario", "candidato"])
                .apply(lambda group: temporal_projection(group, election_date), include_groups=False)
                .reset_index(name="previsto")
            )
            temporal["modelo"] = "baseline_temporal"
            preds.append(temporal)
            bayesian = (
                available.groupby(["cenario", "candidato"])
                .apply(lambda group: fit_latent_forecast(daily_series(group), election_date)[0], include_groups=False)
                .reset_index(name="previsto")
            )
            bayesian["modelo"] = BAYESIAN_MODEL
            preds.append(bayesian)
            pred = pd.concat(preds, ignore_index=True)
            real = latest_rows[["cenario", "candidato", "resultado_real_validos"]].drop_duplicates()
            scored = pred.merge(real, on=["cenario", "candidato"], how="inner")
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


def demo() -> None:
    assert WINDOWS[-1] == 7


def main() -> None:
    demo()
    df = pd.read_csv(PESQUISAS)
    for column in ["ano_eleicao", "dias_campo_ate_eleicao", "amostra", "voto_valido_estimado", "resultado_real_validos"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    result = evaluate(df)
    result.to_csv(OUT, index=False)
    print(f"{len(result)} linhas gravadas em {OUT}")
    if not result.empty:
        print(result.groupby("dias_antes_eleicao")["mae"].mean().to_string())


if __name__ == "__main__":
    main()
