from __future__ import annotations

import csv
import warnings
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf
from sklearn.exceptions import ConvergenceWarning

from catalogo_modelos import FEATURES, FEATURES_NUM, model_catalog

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
PESQUISAS = PROCESSED / "pesquisas_validos.csv"
PREVISOES_BASELINE = PROCESSED / "previsoes.csv"
STATUS = PROCESSED / "modelos_status.csv"
PREVISOES_MODELOS = PROCESSED / "previsoes_modelos.csv"

MIN_ROWS_INFERENCIA = 12
MIN_ROWS_ML = 30


def load_polls() -> pd.DataFrame:
    if not PESQUISAS.exists():
        return pd.DataFrame()
    df = pd.read_csv(PESQUISAS)
    for column in FEATURES_NUM + ["resultado_real_validos", "erro"]:
        if column in df:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    df["cenario_rotulo"] = df.get("cenario_rotulo", df["cenario"]).fillna(df["cenario"])
    return df


def trainable_rows(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "erro" not in df:
        return pd.DataFrame()
    train = df.dropna(subset=["erro", "voto_valido_estimado", "dias_campo_ate_eleicao", "amostra"]).copy()
    for column in ["incumbente", "sucessor_governo", "partido_governo", "reeleicao_permitida", "ex_presidente"]:
        if column in train:
            train[column] = train[column].fillna(0)
    return train


def model_status(modelo: str, status: str, detalhe: str) -> dict[str, str]:
    return {"modelo": modelo, "status": status, "detalhe": detalhe}


def run_inference(train: pd.DataFrame) -> tuple[dict[str, str], object | None]:
    if len(train) < MIN_ROWS_INFERENCIA:
        return model_status("inferencial_ols", "nao_treinado", f"precisa de pelo menos {MIN_ROWS_INFERENCIA} linhas historicas com erro; ha {len(train)}"), None
    formula = "erro ~ voto_valido_estimado + dias_campo_ate_eleicao + amostra + incumbente + sucessor_governo + partido_governo + reeleicao_permitida + ex_presidente + pib_crescimento + inflacao + desemprego + fundamentos_defasagem_max"
    model = smf.ols(formula, data=train).fit()
    return model_status("inferencial_ols", "treinado", f"r2={model.rsquared:.4f}; n={len(train)}"), model


def run_ml(train: pd.DataFrame) -> list[dict[str, str]]:
    if len(train) < MIN_ROWS_ML:
        return [model_status(name, "nao_treinado", f"precisa de pelo menos {MIN_ROWS_ML} linhas historicas com erro; ha {len(train)}") for name in model_catalog()]

    x = train[FEATURES]
    y = train["resultado_real_validos"]

    rows = []
    for name, spec in model_catalog().items():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            spec["model"].fit(x, y)
        rows.append(model_status(name, "treinado", f"familia={spec['familia']}; n={len(train)}; validacao fora da amostra ainda pendente"))
    return rows


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = rows[0].keys() if rows else ["modelo", "status", "detalhe"]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_model_forecasts(status_rows: list[dict[str, str]]) -> None:
    baseline = pd.read_csv(PREVISOES_BASELINE) if PREVISOES_BASELINE.exists() else pd.DataFrame()
    if baseline.empty:
        write_csv([], PREVISOES_MODELOS)
        return

    out = baseline.copy()
    if "modelo" not in out:
        out.insert(0, "modelo", "baseline")
    out["observacao"] = "Modelos inferencial, ML e rede neural aguardam pesquisas historicas para treino."
    out.to_csv(PREVISOES_MODELOS, index=False)


def demo() -> None:
    row = model_status("x", "ok", "teste")
    assert row["modelo"] == "x"
    assert row["status"] == "ok"


def main() -> None:
    demo()
    df = load_polls()
    train = trainable_rows(df)
    status_rows: list[dict[str, str]] = []
    inference_status, _ = run_inference(train)
    status_rows.append(inference_status)
    status_rows.extend(run_ml(train))
    status_rows.append(model_status("ensemble_ia", "parcial", "usa baseline por enquanto; modelos treinados entram quando passarem no backtest"))
    write_csv(status_rows, STATUS)
    write_model_forecasts(status_rows)
    print(f"{len(status_rows)} status gravados em {STATUS}")
    print(f"previsoes comparativas gravadas em {PREVISOES_MODELOS}")


if __name__ == "__main__":
    main()
