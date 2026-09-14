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
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)
        data[col] = data[col] * data["peso"]
    grouped = data.groupby(["data_previsao", "ano_eleicao", "cenario", "candidato"], as_index=False).agg(
        voto_valido_estimado=("voto_valido_estimado", "sum"),
        probabilidade_liderar=("probabilidade_liderar", "sum"),
        probabilidade_ir_ao_segundo_turno=("probabilidade_ir_ao_segundo_turno", "sum"),
        fonte_dados_ate=("fonte_dados_ate", "max"),
    )
    grouped["modelo"] = "ensemble_disciplinado"
    for col in ["voto_valido_estimado", "probabilidade_liderar", "probabilidade_ir_ao_segundo_turno"]:
        grouped[col] = grouped[col].round(4)
    return grouped.sort_values(["cenario", "voto_valido_estimado"], ascending=[True, False])


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
        combine_forecasts(pd.concat(forecasts, ignore_index=True), weights).to_csv(OUT_PREVISAO, index=False)
    print(weights.to_string(index=False))
    print(f"pesos gravados em {OUT}")
    print(f"previsao ensemble gravada em {OUT_PREVISAO}")


if __name__ == "__main__":
    main()
