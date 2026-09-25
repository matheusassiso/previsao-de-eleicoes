from scripts.atualizar_tudo import pipeline


def test_pipeline_only_registers_history_when_requested():
    default = " ".join(" ".join(command) for command in pipeline())
    with_history = " ".join(" ".join(command) for command in pipeline(include_history=True))

    assert "registrar_historico_previsoes.py" not in default
    assert "registrar_historico_previsoes.py" in with_history
    assert default.index("preparar_dados.py") < default.index("gerar_ensemble.py")
