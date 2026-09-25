from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"

RECENT_AUDIT = RAW / "auditoria_2026_recente.csv"
OUT_CSV = PROCESSED / "pendencias_operacionais.csv"
OUT_MD = DOCS / "pendencias-operacionais.md"


def pending_recent_audit(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["prioridade", "tipo", "item", "detalhe", "fonte_atual"])
    status = df["status_auditoria"].astype(str)
    weak = status.str.contains("pendente|agregador|sem_fonte|sem fonte", case=False, na=False)
    pending = df.loc[weak].copy()
    pending["prioridade"] = pending["status_auditoria"].map(
        lambda value: "alta" if "pendente" in str(value) or "sem_fonte" in str(value) else "media"
    )
    pending["tipo"] = "resolver auditoria insuficiente"
    pending["item"] = pending["instituto"].astype(str) + " " + pending["data_publicacao"].astype(str)
    pending["detalhe"] = pending["observacao_auditoria"].fillna("")
    pending["fonte_atual"] = pending["fonte_auditoria"].fillna("")
    return pending[["prioridade", "tipo", "item", "detalhe", "fonte_atual"]].sort_values(["prioridade", "item"])


def write_markdown(pending: pd.DataFrame) -> None:
    lines = ["# Pendencias operacionais", ""]
    if pending.empty:
        lines.append("Nenhuma pendencia operacional encontrada nos filtros atuais.")
    else:
        lines.append(f"- Pendencias abertas: {len(pending)}.")
        lines.append("- Prioridade alta: falta registro, metodologia ou fonte verificavel.")
        lines.append("- Prioridade media: a fonte ainda depende de agregador publico ou precisa de conferencia manual.")
        lines.append("")
        for row in pending.to_dict("records"):
            lines.append(f"- **{row['prioridade']}** | {row['item']}: {row['tipo']}. {row['detalhe']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    audit = pd.read_csv(RECENT_AUDIT) if RECENT_AUDIT.exists() else pd.DataFrame()
    pending = pending_recent_audit(audit)
    pending.to_csv(OUT_CSV, index=False)
    write_markdown(pending)
    print(f"{len(pending)} pendencias gravadas em {OUT_CSV}")


if __name__ == "__main__":
    main()
