from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
BACKTEST = PROCESSED / "backtest_modelos.csv"
BACKTEST_VIVO = PROCESSED / "backtest_previsao_viva.csv"
PREVISOES_MODELOS = PROCESSED / "previsoes_modelos.csv"
PREVISOES = PROCESSED / "previsoes.csv"
BAYESIAN = PROCESSED / "previsao_bayesiana_dinamica.csv"
ROLLING_2026 = PROCESSED / "rolling_previsao_2026.csv"
OUT = PROCESSED / "ensemble_pesos.csv"
OUT_PREVISAO = PROCESSED / "previsao_ensemble.csv"


def compute_weights(backtest: pd.DataFrame, live_backtest: pd.DataFrame | None = None) -> pd.DataFrame:
    summary = backtest.groupby("modelo", as_index=False)["mae"].mean()
    baseline = float(summary.loc[summary["modelo"] == "baseline_pesquisa", "mae"].iloc[0])
    accepted = summary[summary["mae"] <= baseline].copy()
    if live_backtest is not None and not live_backtest.empty:
        live = live_backtest.groupby("modelo", as_index=False)["mae"].mean()
        live_baseline = live.loc[live["modelo"] == "baseline_pesquisa", "mae"]
        live_bayesian = live.loc[live["modelo"] == "bayesiano_dinamico_kalman", "mae"]
        if not live_baseline.empty and not live_bayesian.empty and float(live_bayesian.iloc[0]) <= float(live_baseline.iloc[0]):
            accepted = pd.concat(
                [
                    accepted,
                    pd.DataFrame([{"modelo": "bayesiano_dinamico_kalman", "mae": max(baseline, float(live_bayesian.iloc[0]))}]),
                ],
                ignore_index=True,
            )
    accepted["peso_bruto"] = 1 / accepted["mae"].clip(lower=0.001)
    accepted["peso"] = accepted["peso_bruto"] / accepted["peso_bruto"].sum()
    return accepted[["modelo", "mae", "peso"]].sort_values("peso", ascending=False)


def combine_forecasts(forecasts: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    if forecasts.empty or weights.empty:
        return pd.DataFrame()
    cols = ["voto_valido_estimado", "probabilidade_liderar", "probabilidade_ir_ao_segundo_turno"]
    data = forecasts.merge(weights[["modelo", "peso"]], on="modelo", how="inner").copy()
    if data.empty:
        return pd.DataFrame()
    for col in cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")
        data[f"_{col}_valor"] = data[col].fillna(0) * data["peso"]
        data[f"_{col}_peso"] = data["peso"].where(data[col].notna(), 0)
    grouped = data.groupby(["data_previsao", "ano_eleicao", "cenario", "candidato"], as_index=False).agg(
        voto_valido_estimado=("_voto_valido_estimado_valor", "sum"),
        voto_peso=("_voto_valido_estimado_peso", "sum"),
        probabilidade_liderar=("_probabilidade_liderar_valor", "sum"),
        liderar_peso=("_probabilidade_liderar_peso", "sum"),
        probabilidade_ir_ao_segundo_turno=("_probabilidade_ir_ao_segundo_turno_valor", "sum"),
        segundo_turno_peso=("_probabilidade_ir_ao_segundo_turno_peso", "sum"),
        fonte_dados_ate=("fonte_dados_ate", "max"),
    )
    grouped["voto_valido_estimado"] = grouped["voto_valido_estimado"] / grouped["voto_peso"].replace(0, pd.NA)
    grouped["probabilidade_liderar"] = grouped["probabilidade_liderar"] / grouped["liderar_peso"].replace(0, pd.NA)
    grouped["probabilidade_ir_ao_segundo_turno"] = grouped["probabilidade_ir_ao_segundo_turno"] / grouped["segundo_turno_peso"].replace(0, pd.NA)
    grouped = grouped.drop(columns=["voto_peso", "liderar_peso", "segundo_turno_peso"])
    grouped["modelo"] = "ensemble_disciplinado"
    for col in ["voto_valido_estimado", "probabilidade_liderar", "probabilidade_ir_ao_segundo_turno"]:
        grouped[col] = pd.to_numeric(grouped[col], errors="coerce").round(4)
    return grouped.sort_values(["cenario", "voto_valido_estimado"], ascending=[True, False])


def rolling_forecasts(path: Path, reference: pd.DataFrame) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    rolling = pd.read_csv(path)
    if rolling.empty:
        return pd.DataFrame()
    data_previsao = str(reference["data_previsao"].max()) if "data_previsao" in reference else ""
    fonte_dados_ate = str(reference["fonte_dados_ate"].max()) if "fonte_dados_ate" in reference else data_previsao
    out = rolling.rename(columns={"cenario_rotulo": "cenario", "previsto": "voto_valido_estimado"}).copy()
    out["data_previsao"] = data_previsao
    out["fonte_dados_ate"] = fonte_dados_ate
    out["probabilidade_liderar"] = pd.NA
    out["probabilidade_ir_ao_segundo_turno"] = pd.NA
    return out[
        [
            "data_previsao",
            "ano_eleicao",
            "cenario",
            "modelo",
            "candidato",
            "voto_valido_estimado",
            "probabilidade_liderar",
            "probabilidade_ir_ao_segundo_turno",
            "fonte_dados_ate",
        ]
    ]


def demo() -> None:
    df = pd.DataFrame({"modelo": ["baseline_pesquisa", "x"], "mae": [10.0, 5.0]})
    out = compute_weights(df)
    assert set(out["modelo"]) == {"baseline_pesquisa", "x"}
    assert round(out["peso"].sum(), 6) == 1
    forecasts = pd.DataFrame(
        [
            {"data_previsao": "2026-01-01", "ano_eleicao": 2026, "cenario": "A", "candidato": "X", "modelo": "baseline_pesquisa", "voto_valido_estimado": 40, "probabilidade_liderar": 0.2, "probabilidade_ir_ao_segundo_turno": 1, "fonte_dados_ate": "2026-01-01"},
            {"data_previsao": "2026-01-01", "ano_eleicao": 2026, "cenario": "A", "candidato": "X", "modelo": "x", "voto_valido_estimado": 50, "probabilidade_liderar": 0.8, "probabilidade_ir_ao_segundo_turno": 1, "fonte_dados_ate": "2026-01-01"},
        ]
    )
    assert round(float(combine_forecasts(forecasts, out).iloc[0]["voto_valido_estimado"]), 2) == 46.67
    live = pd.DataFrame({"modelo": ["baseline_pesquisa", "bayesiano_dinamico_kalman"], "mae": [8.0, 7.0]})
    assert "bayesiano_dinamico_kalman" in set(compute_weights(df, live)["modelo"])


def main() -> None:
    demo()
    if not BACKTEST.exists():
        pd.DataFrame(columns=["modelo", "mae", "peso"]).to_csv(OUT, index=False)
        print(f"sem backtest; pesos vazios em {OUT}")
        return
    live = pd.read_csv(BACKTEST_VIVO) if BACKTEST_VIVO.exists() else None
    weights = compute_weights(pd.read_csv(BACKTEST), live)
    weights.to_csv(OUT, index=False)
    if PREVISOES.exists():
        forecasts = [pd.read_csv(PREVISOES)]
        if BAYESIAN.exists():
            forecasts.append(pd.read_csv(BAYESIAN))
        rolling = rolling_forecasts(ROLLING_2026, forecasts[0])
        if not rolling.empty:
            forecasts.append(rolling)
        combine_forecasts(pd.concat(forecasts, ignore_index=True), weights).to_csv(OUT_PREVISAO, index=False)
    print(weights.to_string(index=False))
    print(f"pesos gravados em {OUT}")
    print(f"previsao ensemble gravada em {OUT_PREVISAO}")


if __name__ == "__main__":
    main()
