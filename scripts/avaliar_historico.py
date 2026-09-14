from __future__ import annotations

from pathlib import Path
import warnings

import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.exceptions import ConvergenceWarning

from ajustes_literatura import adjusted_vote, house_effect_lookup, house_effect_stats, house_effect_vote, institute_stats, stats_lookup
from catalogo_modelos import FEATURES, FEATURES_NUM, model_catalog
ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
PESQUISAS = PROCESSED / "pesquisas_validos.csv"
OUT = PROCESSED / "backtest_modelos.csv"
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

def load_data() -> pd.DataFrame:
    df = pd.read_csv(PESQUISAS)
    for column in FEATURES_NUM + ["resultado_real_validos"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df[FEATURES_NUM] = df[FEATURES_NUM].fillna(0)
    df["cenario_rotulo"] = df.get("cenario_rotulo", df["cenario"]).fillna(df["cenario"])
    return df.dropna(subset=["resultado_real_validos", "voto_valido_estimado", "dias_campo_ate_eleicao", "amostra"])


def evaluate(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    years = sorted(int(year) for year in df["ano_eleicao"].unique())
    for year in years:
        train = df[df["ano_eleicao"] != year]
        test = df[df["ano_eleicao"] == year]
        if train.empty or test.empty:
            continue
        rows.append(
            {
                "ano_teste": year,
                "modelo": "baseline_pesquisa",
                "linhas_treino": len(train),
                "linhas_teste": len(test),
                "mae": mean_absolute_error(test["resultado_real_validos"], test["voto_valido_estimado"]),
            }
        )
        lookup = stats_lookup(institute_stats(train))
        adjusted = test.apply(lambda row: adjusted_vote(row, lookup), axis=1)
        house_lookup = house_effect_lookup(house_effect_stats(train))
        house = test.apply(lambda row: house_effect_vote(row, house_lookup, lookup), axis=1)
        rows.append(
            {
                "ano_teste": year,
                "modelo": "baseline_ajustado",
                "linhas_treino": len(train),
                "linhas_teste": len(test),
                "mae": mean_absolute_error(test["resultado_real_validos"], adjusted),
            }
        )
        rows.append(
            {
                "ano_teste": year,
                "modelo": "baseline_efeito_casa",
                "linhas_treino": len(train),
                "linhas_teste": len(test),
                "mae": mean_absolute_error(test["resultado_real_validos"], house),
            }
        )
        catalog = model_catalog()
        for name in EVAL_MODELS:
            spec = catalog[name]
            print(f"avaliando {year}: {name}", flush=True)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ConvergenceWarning)
                spec["model"].fit(train[FEATURES], train["resultado_real_validos"])
            pred = spec["model"].predict(test[FEATURES]).clip(0, 100)
            rows.append(
                {
                    "ano_teste": year,
                    "modelo": name,
                    "linhas_treino": len(train),
                    "linhas_teste": len(test),
                    "mae": mean_absolute_error(test["resultado_real_validos"], pred),
                }
            )
    return pd.DataFrame(rows)


def demo() -> None:
    assert "voto_valido_estimado" in FEATURES
    assert "instituto" in FEATURES
    assert "mlp_pequena" in EVAL_MODELS


def main() -> None:
    demo()
    df = load_data()
    result = evaluate(df)
    result.to_csv(OUT, index=False)
    print(f"{len(result)} linhas gravadas em {OUT}")
    if not result.empty:
        print(result.groupby("modelo")["mae"].mean().sort_values().to_string())


if __name__ == "__main__":
    main()
