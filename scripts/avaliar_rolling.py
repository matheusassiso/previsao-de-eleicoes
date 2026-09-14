from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import mean_absolute_error

from ajustes_literatura import adjusted_vote, house_effect_lookup, house_effect_stats, house_effect_vote, institute_stats, stats_lookup
from catalogo_modelos import FEATURES, FEATURES_NUM, model_catalog

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
PESQUISAS = PROCESSED / "pesquisas_validos.csv"
OUT_COMPARACAO = PROCESSED / "rolling_comparacao.csv"
OUT_PREVISAO_2026 = PROCESSED / "rolling_previsao_2026.csv"
OUT_RESUMO = PROCESSED / "rolling_resumo_modelos.csv"

HISTORIC_TARGETS = [2010, 2014, 2018, 2022]
EVAL_MODELS = [
    "ridge",
    "huber",
    "random_forest_07_600",
    "extra_trees",
    "gradient_boosting",
    "mlp_pequena",
    "voting_ia",
    "stacking_ia",
]


def chronological_splits(df: pd.DataFrame, targets: list[int] = HISTORIC_TARGETS):
    years = sorted(int(year) for year in df["ano_eleicao"].dropna().unique())
    for target in targets:
        train_years = [year for year in years if year < target]
        if train_years:
            yield target, df[df["ano_eleicao"].isin(train_years)].copy(), df[df["ano_eleicao"] == target].copy()


def load_data() -> pd.DataFrame:
    df = pd.read_csv(PESQUISAS)
    for column in FEATURES_NUM + ["ano_eleicao", "resultado_real_validos"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df[FEATURES_NUM] = df[FEATURES_NUM].fillna(0)
    df["cenario_rotulo"] = df.get("cenario_rotulo", df["cenario"]).fillna(df["cenario"])
    return df


def latest_poll_rows(df: pd.DataFrame) -> pd.DataFrame:
    key = ["ano_eleicao", "cenario_rotulo", "candidato"]
    latest = df.groupby(key)["data_publicacao"].transform("max")
    return df[df["data_publicacao"] == latest].copy()


def aggregate_prediction(df: pd.DataFrame, value_col: str, model_name: str) -> pd.DataFrame:
    work = latest_poll_rows(df)
    weights = work["amostra"].clip(lower=1) ** 0.5
    work["_weighted"] = work[value_col] * weights
    grouped = work.groupby(["ano_eleicao", "cenario_rotulo", "candidato"], as_index=False).agg(
        previsto=("_weighted", "sum"),
        peso=("amostra", lambda values: sum(values.clip(lower=1) ** 0.5)),
        resultado_real_validos=("resultado_real_validos", "first"),
    )
    grouped["previsto"] = grouped["previsto"] / grouped["peso"]
    grouped["modelo"] = model_name
    return grouped.drop(columns=["peso"])


def ols_prediction(train: pd.DataFrame, test: pd.DataFrame) -> pd.Series:
    formula = "resultado_real_validos ~ voto_valido_estimado + dias_campo_ate_eleicao + amostra + incumbente + sucessor_governo + partido_governo + reeleicao_permitida + ex_presidente"
    model = smf.ols(formula, data=train).fit()
    return model.predict(test).clip(0, 100)


def model_predictions(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    train = train.dropna(subset=["resultado_real_validos", "voto_valido_estimado"])
    predictions = [aggregate_prediction(test, "voto_valido_estimado", "baseline_pesquisa")]
    lookup = stats_lookup(institute_stats(train))
    adjusted = test.copy()
    adjusted["_ajustado"] = adjusted.apply(lambda row: adjusted_vote(row, lookup), axis=1)
    house_lookup = house_effect_lookup(house_effect_stats(train))
    adjusted["_efeito_casa"] = adjusted.apply(lambda row: house_effect_vote(row, house_lookup, lookup), axis=1)
    predictions.append(aggregate_prediction(adjusted, "_ajustado", "baseline_ajustado"))
    predictions.append(aggregate_prediction(adjusted, "_efeito_casa", "baseline_efeito_casa"))
    if len(train) >= 30:
        scored = test.copy()
        scored["_pred"] = ols_prediction(train, scored)
        predictions.append(aggregate_prediction(scored, "_pred", "inferencial_ols"))
    catalog = model_catalog()
    for name in EVAL_MODELS:
        if len(train) < 30:
            continue
        spec = catalog[name]
        print(f"treinando {name}: treino={len(train)} teste={len(test)}", flush=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            spec["model"].fit(train[FEATURES], train["resultado_real_validos"])
        scored = test.copy()
        scored["_pred"] = spec["model"].predict(scored[FEATURES]).clip(0, 100)
        predictions.append(aggregate_prediction(scored, "_pred", name))
    return pd.concat(predictions, ignore_index=True)


def rolling_backtest(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for target, train, test in chronological_splits(df):
        preds = model_predictions(train, test.dropna(subset=["resultado_real_validos"]))
        preds["ano_treino_max"] = int(train["ano_eleicao"].max())
        preds["erro_abs"] = (preds["resultado_real_validos"] - preds["previsto"]).abs()
        rows.append(preds)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def rolling_summary(comparison: pd.DataFrame) -> pd.DataFrame:
    if comparison.empty:
        return pd.DataFrame(columns=["ano_teste", "modelo", "mae"])
    return (
        comparison.groupby(["ano_eleicao", "modelo"], as_index=False)["erro_abs"]
        .mean()
        .rename(columns={"ano_eleicao": "ano_teste", "erro_abs": "mae"})
        .sort_values(["ano_teste", "mae"])
    )


def forecast_2026(df: pd.DataFrame) -> pd.DataFrame:
    train = df[(df["ano_eleicao"] < 2026) & df["resultado_real_validos"].notna()].copy()
    test = df[(df["ano_eleicao"] == 2026) & (df.get("usar_previsao_principal", 1).astype(str) != "0")].copy()
    if train.empty or test.empty:
        return pd.DataFrame()
    out = model_predictions(train, test)
    out["ano_treino_max"] = int(train["ano_eleicao"].max())
    return out.drop(columns=["resultado_real_validos"])


def main() -> None:
    df = load_data()
    comparison = rolling_backtest(df)
    summary = rolling_summary(comparison)
    prediction_2026 = forecast_2026(df)
    comparison.to_csv(OUT_COMPARACAO, index=False)
    summary.to_csv(OUT_RESUMO, index=False)
    prediction_2026.to_csv(OUT_PREVISAO_2026, index=False)
    print(f"{len(comparison)} linhas gravadas em {OUT_COMPARACAO}")
    print(summary.to_string(index=False))
    print(f"{len(prediction_2026)} previsoes 2026 gravadas em {OUT_PREVISAO_2026}")


if __name__ == "__main__":
    main()
