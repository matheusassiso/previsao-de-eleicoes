from __future__ import annotations

import math
from datetime import date, datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
PESQUISAS = PROCESSED / "pesquisas_validos.csv"
OUT_QUALIDADE = PROCESSED / "qualidade_institutos.csv"
OUT_EFEITO_CASA = PROCESSED / "efeito_casa_instituto_candidato.csv"

HALF_LIFE_DAYS = 21
DEFAULT_MAE = 8.0
MIN_ROWS = 10
MIN_HOUSE_ROWS = 3
MAX_TREND_ADJUSTMENT = 5.0


def parse_date(value: str) -> date:
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def clip(value: float) -> float:
    return min(100.0, max(0.0, value))


def institute_stats(df: pd.DataFrame) -> pd.DataFrame:
    historic = df.dropna(subset=["resultado_real_validos", "voto_valido_estimado"]).copy()
    historic["erro"] = historic["resultado_real_validos"] - historic["voto_valido_estimado"]
    historic["erro_abs"] = historic["erro"].abs()
    stats = (
        historic.groupby("instituto", as_index=False)
        .agg(linhas=("erro", "size"), vies_medio=("erro", "mean"), mae=("erro_abs", "mean"))
        .sort_values(["mae", "linhas"], ascending=[True, False])
    )
    return stats


def stats_lookup(stats: pd.DataFrame) -> dict[str, dict[str, float]]:
    if stats.empty:
        return {}
    return {
        str(row.instituto): {"linhas": float(row.linhas), "vies_medio": float(row.vies_medio), "mae": float(row.mae)}
        for row in stats.itertuples()
    }


def house_effect_stats(df: pd.DataFrame, min_rows: int = MIN_HOUSE_ROWS) -> pd.DataFrame:
    historic = df.dropna(subset=["resultado_real_validos", "voto_valido_estimado"]).copy()
    historic["erro"] = historic["resultado_real_validos"] - historic["voto_valido_estimado"]
    historic["erro_abs"] = historic["erro"].abs()
    stats = (
        historic.groupby(["instituto", "candidato"], as_index=False)
        .agg(linhas=("erro", "size"), vies_medio=("erro", "mean"), mae=("erro_abs", "mean"))
    )
    return stats[stats["linhas"] >= min_rows].sort_values(["mae", "linhas"], ascending=[True, False])


def house_effect_lookup(stats: pd.DataFrame) -> dict[tuple[str, str], dict[str, float]]:
    if stats.empty:
        return {}
    return {
        (str(row.instituto), str(row.candidato)): {"linhas": float(row.linhas), "vies_medio": float(row.vies_medio), "mae": float(row.mae)}
        for row in stats.itertuples()
    }


def adjusted_vote(row: pd.Series | dict, lookup: dict[str, dict[str, float]]) -> float:
    estimate = float(row["voto_valido_estimado"])
    info = lookup.get(str(row.get("instituto", "")))
    if not info or info["linhas"] < MIN_ROWS:
        return estimate
    return clip(estimate + info["vies_medio"])


def house_effect_vote(row: pd.Series | dict, lookup: dict[tuple[str, str], dict[str, float]], fallback: dict[str, dict[str, float]] | None = None) -> float:
    estimate = float(row["voto_valido_estimado"])
    info = lookup.get((str(row.get("instituto", "")), str(row.get("candidato", ""))))
    if info:
        return clip(estimate + info["vies_medio"])
    return adjusted_vote(row, fallback or {})


def quality_multiplier(row: pd.Series | dict, lookup: dict[str, dict[str, float]]) -> float:
    info = lookup.get(str(row.get("instituto", "")))
    if not info or info["linhas"] < MIN_ROWS:
        return 1.0
    return max(0.5, min(1.5, 2 * DEFAULT_MAE / (DEFAULT_MAE + info["mae"])))


def poll_weight(row: pd.Series | dict, forecast_date: date, lookup: dict[str, dict[str, float]] | None = None) -> float:
    age_days = max((forecast_date - parse_date(row["data_publicacao"])).days, 0)
    recency = math.exp(-age_days / HALF_LIFE_DAYS)
    sample = math.sqrt(max(float(row["amostra"]), 1))
    quality = quality_multiplier(row, lookup or {})
    return recency * sample * quality


def weighted_average(group: pd.DataFrame, value_col: str = "voto_valido_estimado") -> float:
    weights = group["amostra"].clip(lower=1) ** 0.5
    return float((group[value_col] * weights).sum() / weights.sum())


def temporal_projection(group: pd.DataFrame, election_date: str | date, value_col: str = "voto_valido_estimado") -> float:
    if group.empty:
        return 0.0
    work = group.copy()
    work["data_publicacao"] = pd.to_datetime(work["data_publicacao"])
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    work["amostra"] = pd.to_numeric(work["amostra"], errors="coerce").fillna(1000)
    work = work.dropna(subset=[value_col, "data_publicacao"])
    base = weighted_average(work, value_col)
    if len(work["data_publicacao"].drop_duplicates()) < 2:
        return clip(base)
    first = work["data_publicacao"].min()
    x = (work["data_publicacao"] - first).dt.days.astype(float)
    y = work[value_col].astype(float)
    weights = work["amostra"].clip(lower=1) ** 0.5
    x_bar = float((x * weights).sum() / weights.sum())
    y_bar = float((y * weights).sum() / weights.sum())
    denom = float((((x - x_bar) ** 2) * weights).sum())
    if denom == 0:
        return clip(base)
    slope = float(((x - x_bar) * (y - y_bar) * weights).sum() / denom)
    target_date = pd.to_datetime(election_date)
    latest = work["data_publicacao"].max()
    adjustment = slope * max((target_date - latest).days, 0)
    adjustment = max(-MAX_TREND_ADJUSTMENT, min(MAX_TREND_ADJUSTMENT, adjustment))
    return clip(base + adjustment)


def write_quality_table(df: pd.DataFrame, path: Path = OUT_QUALIDADE) -> pd.DataFrame:
    stats = institute_stats(df)
    path.parent.mkdir(parents=True, exist_ok=True)
    stats.to_csv(path, index=False)
    return stats


def write_house_effect_table(df: pd.DataFrame, path: Path = OUT_EFEITO_CASA) -> pd.DataFrame:
    stats = house_effect_stats(df)
    path.parent.mkdir(parents=True, exist_ok=True)
    stats.to_csv(path, index=False)
    return stats


def demo() -> None:
    df = pd.DataFrame(
        [
            {"instituto": "A", "voto_valido_estimado": 40, "resultado_real_validos": 45},
            {"instituto": "A", "voto_valido_estimado": 50, "resultado_real_validos": 45},
        ]
    )
    stats = institute_stats(df)
    assert round(float(stats.iloc[0]["mae"]), 1) == 5.0
    house = house_effect_lookup(house_effect_stats(df, min_rows=2))
    assert house_effect_vote({"instituto": "A", "candidato": "", "voto_valido_estimado": 50}, {}, stats_lookup(stats)) == 50
    assert temporal_projection(pd.DataFrame([{"data_publicacao": "2026-01-01", "voto_valido_estimado": 40, "amostra": 1000}]), "2026-10-04") == 40


if __name__ == "__main__":
    demo()
    data = pd.read_csv(PESQUISAS)
    for column in ["voto_valido_estimado", "resultado_real_validos"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    stats = write_quality_table(data)
    house = write_house_effect_table(data)
    print(f"{len(stats)} institutos gravados em {OUT_QUALIDADE}")
    print(f"{len(house)} efeitos casa gravados em {OUT_EFEITO_CASA}")
