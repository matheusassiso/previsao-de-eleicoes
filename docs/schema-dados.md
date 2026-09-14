# Schema dos dados

## `data/raw/pesquisas.csv`

Uma linha por candidato, pesquisa e cenario.

Campos atuais:

- `ano_eleicao`: ano da eleicao.
- `turno`: turno pesquisado, normalmente `1`.
- `instituto`: instituto responsavel.
- `data_inicio_campo`: inicio da coleta, em `AAAA-MM-DD`.
- `data_fim_campo`: fim da coleta, em `AAAA-MM-DD`.
- `data_publicacao`: data de publicacao, em `AAAA-MM-DD`.
- `amostra`: numero de entrevistados.
- `cenario`: identificador textual do cenario.
- `candidato`: nome padronizado do candidato.
- `percentual_total`: intencao de voto no total dos entrevistados.
- `brancos_nulos`: percentual de brancos e nulos na pesquisa.
- `indecisos`: percentual de indecisos.
- `fonte`: link ou referencia da fonte.

## `data/raw/resultados_primeiro_turno.csv`

Uma linha por candidato e ano.

Campos atuais:

- `ano_eleicao`
- `candidato`
- `percentual_validos`
- `fonte`

## `data/raw/eleicoes.csv`

Uma linha por eleicao presidencial.

Campos:

- `ano_eleicao`
- `data_primeiro_turno`
- `presidente_incumbente`
- `partido_governo`
- `reeleicao_permitida`
- `observacao`

## `data/processed/pesquisas_validos.csv`

Gerado por `scripts/preparar_dados.py`.

Campos principais:

- todos os campos de `pesquisas.csv`;
- `voto_valido_estimado`: percentual convertido para votos validos;
- `dias_campo_ate_eleicao`: dias entre o fim do campo e o primeiro turno;
- `dias_publicacao_ate_eleicao`: dias entre a publicacao e o primeiro turno;
- `ordem_pesquisa_instituto_cenario`: sequencia da pesquisa para o mesmo instituto e cenario;
- `ordem_pesquisa_campanha`: sequencia geral da pesquisa na campanha;
- `resultado_real_validos`: resultado oficial, quando conhecido;
- `erro`: resultado real menos estimativa da pesquisa, quando conhecido.

## `data/processed/previsoes.csv`

Gerado por `scripts/prever.py`.

Uma linha por candidato e rodada de previsao.

Campos:

- `data_previsao`
- `ano_eleicao`
- `cenario`
- `candidato`
- `voto_valido_estimado`
- `intervalo_baixo`
- `intervalo_alto`
- `probabilidade_liderar`
- `probabilidade_ir_ao_segundo_turno`
- `fonte_dados_ate`

## `data/processed/previsao_bayesiana_dinamica.csv`

Gerado por `scripts/bayesiano_dinamico.py`.

Uma linha por candidato e cenario principal de 2026. Campos iguais a `previsoes.csv`, com uma coluna adicional:

- `metodo_estado_latente`: indica se a serie usou Kalman de tendencia local ou fallback por poucos pontos.

## `data/processed/auditoria_fontes.csv`

Gerado por `scripts/auditar_fontes.py`.

Uma linha por ano e fonte, com contagens de linhas, pesquisas unicas, institutos, amostras imputadas e valores fora do intervalo 0-100.

## Variaveis estruturais futuras

Entram depois que houver dados suficientes:

- `incumbente`
- `sucessor_governo`
- `partido_governo`
- `reeleicao_permitida`
- `ex_presidente`
- `oposicao_principal`
- `candidato_governista_sem_incumbente`

## `data/raw/variaveis_candidatos.csv`

Uma linha por candidato relevante e ano.

Campos:

- `ano_eleicao`
- `candidato`
- `incumbente`
- `sucessor_governo`
- `partido_governo`
- `reeleicao_permitida`
- `ex_presidente`
- `observacao`

## `data/raw/cenarios.csv`

Uma linha por cenario extraido.

Campos:

- `ano_eleicao`
- `cenario`
- `rotulo`
- `prioridade`
- `usar_previsao_principal`
- `observacao`

Essa tabela evita que a previsao principal misture cenarios alternativos, antigos ou reduzidos.

## `data/raw/pesquisas_2026_iniciais.csv`

Base auxiliar com pesquisas atuais coletadas a partir de resumos publicados. Serve para teste inicial do pipeline, mas deve ser validada contra PesqEle/TSE e fonte primaria antes de entrar no arquivo principal.

## Variaveis de segundo modelo

Ficam fora do baseline ate existir base suficiente:

- `campo_politico`
- `alinhamento_governo`
- `polarizacao`
- `transferencia_presidencial`
- `rejeicao`
- `conhecimento`
- `aprovacao_governo`
- `economia`
- `evento_relevante`
