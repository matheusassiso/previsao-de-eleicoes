import pandas as pd

from scripts.gerar_pendencias import pending_recent_audit


def test_pending_recent_audit_keeps_rows_without_primary_source():
    df = pd.DataFrame(
        [
            {"instituto": "A", "data_publicacao": "2026-09-01", "status_auditoria": "fonte_primaria_confirmada", "observacao_auditoria": "", "fonte_auditoria": ""},
            {"instituto": "B", "data_publicacao": "2026-09-02", "status_auditoria": "registro_e_metodologia_confirmados_secundaria", "observacao_auditoria": "falta primaria", "fonte_auditoria": "https://x"},
        ]
    )

    out = pending_recent_audit(df)

    assert out["item"].tolist() == ["B 2026-09-02"]
    assert out["prioridade"].tolist() == ["alta"]
