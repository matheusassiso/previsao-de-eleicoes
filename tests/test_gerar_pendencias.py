import pandas as pd

from scripts.gerar_pendencias import pending_recent_audit


def test_pending_recent_audit_keeps_only_weak_audit_rows():
    df = pd.DataFrame(
        [
            {"instituto": "A", "data_publicacao": "2026-09-01", "status_auditoria": "fonte_primaria_confirmada", "observacao_auditoria": "", "fonte_auditoria": ""},
            {"instituto": "B", "data_publicacao": "2026-09-02", "status_auditoria": "registro_e_metodologia_confirmados_secundaria", "observacao_auditoria": "falta primaria", "fonte_auditoria": "https://x"},
            {"instituto": "C", "data_publicacao": "2026-09-03", "status_auditoria": "registro_em_agregador_publico", "observacao_auditoria": "fraco", "fonte_auditoria": "https://y"},
        ]
    )

    out = pending_recent_audit(df)

    assert out["item"].tolist() == ["C 2026-09-03"]
    assert out["prioridade"].tolist() == ["media"]
