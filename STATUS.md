# Status atual

Atualizado em 2026-09-25.

## Pronto

- Estrutura do projeto dentro de `Documents/Codex/previsao-de-eleicoes`.
- Schema dos dados.
- Documento de processo e modelagem.
- Documento de referencias.
- Revisao de literatura sobre metodos de previsao eleitoral.
- Relatorio Quarto renderizado em HTML.
- Relatorio melhorado visualmente com resumo executivo, cobertura por ano e graficos mais focados no cenario recente.
- Relatorio reorganizado com resultado atual no inicio, tabela de cenarios de 2026, status dos modelos e tabelas longas reduzidas para recortes legiveis.
- Secao "O que mudou com as pesquisas novas" adicionada ao relatorio, comparando cenario anterior e coleta recente de agosto/setembro.
- Secao "Confianca da rodada" adicionada ao relatorio, combinando recencia, cobertura, auditoria, margem e erro historico.
- Cenario operacional de 2026 corrigido: apenas `agosto_setembro_2026_sem_marcal` fica como previsao principal; cenarios antigos/ampliados e com Pablo Marcal ficam como comparativos.
- Tabela de backtest cronologico por vencedor prevista no relatorio, comparando vencedor previsto, vencedor real, acerto e MAE por modelo.
- Auditoria das pesquisas recentes de 2026 adicionada com registro TSE, fonte de auditoria e status por instituto/data/cenario.
- Notebook Jupyter gerado por script.
- Scripts para preparar pesquisas e gerar previsao baseline.
- Scripts para coletar e normalizar pesquisas historicas estruturadas da Wikipedia.
- Script para extrair pesquisas de primeiro turno de 2006 em graficos de wikitexto.
- Ajuste de eficiencia inspirado na literatura: qualidade historica do instituto, vies medio e baseline ajustado.
- Efeito casa por instituto-candidato.
- Previsao final por ensemble disciplinado.
- Fundamentos economicos objetivos por eleicao: PIB, inflacao e desemprego pre-eleicao.
- Baseline temporal simples para previsao viva e backtest por janelas.
- Modelo Bayesiano dinamico por estado latente via filtro de Kalman para 2026.
- Auditoria automatica de cobertura e qualidade basica por ano/fonte.
- Intervalos e probabilidades calibrados pelo erro historico dos modelos.
- Script para rodar modelos inferencial, machine learning, rede neural simples e ensemble.
- Catalogo ampliado com 10 modelos de machine learning, 3 modelos de deep learning tabular e 2 ensembles de IA.
- Resultados historicos do primeiro turno de 1994 a 2022 em CSV inicial.
- Calendario eleitoral de 1994 a 2026.
- Variaveis estruturais iniciais por candidato.
- Base limpa automatica com 1.255 linhas brutas aproveitaveis de 2010 a 2026.
- Complemento manual auditado de 1994 e 1998 com pesquisas Datafolha publicadas pela Folha.
- Series consolidadas Datafolha de 1994 e 1998 incorporadas, adicionando 23 pesquisas/cenarios historicos sem duplicar datas ja auditadas.
- Complemento manual auditado de 1994 e 2006 com pesquisas publicadas pela Folha.
- Complemento de 2002 com 6 linhas de pesquisa nacional CESOP/Datafolha e 367 linhas do acervo Fernando Rodrigues/UOL.
- Complemento de 2006 com 14 linhas extraidas de wikitexto.
- Complemento recente de 2026 com 231 linhas de pesquisas de agosto/setembro incluindo Renan Santos, candidatos menores e cenarios alternativos com Pablo Marcal.
- Base processada com 1.965 linhas de pesquisas ate o primeiro turno.
- Historico de previsoes criado em `data/processed/previsoes_historico.csv`.
- Tabela de qualidade historica com 55 institutos apos limpeza de marcadores de referencia.
- Tabela de efeito casa com 95 pares instituto-candidato.
- Previsao ensemble em `data/processed/previsao_ensemble.csv`.
- Fundamentos economicos em `data/raw/fundamentos_eleicao.csv`.
- Tabela de cenarios com rotulos legiveis e flag de previsao principal.
- Backtest por janelas de tempo antes da eleicao.
- Backtest de previsao viva usando apenas pesquisas ja publicadas em cada corte, incluindo o Bayesiano dinamico.
- Avaliacao cronologica: treina no passado, preve 2010, 2014, 2018 e 2022, e aplica em 2026.
- Backtests pesados otimizados com catalogo representativo de modelos, mantendo baseline, inferencia, ML, deep learning e IA.

## Cobertura processada

- 1994: 71 linhas.
- 1998: 41 linhas.
- 2002: 373 linhas.
- 2006: 32 linhas.
- 2010: 170 linhas.
- 2014: 54 linhas.
- 2018: 170 linhas.
- 2022: 474 linhas.
- 2026: 580 linhas.

## Modelos

- `inferencial_ols`: treinado.
- `baseline_ajustado`: baseline com correcao por vies historico do instituto quando ha amostra suficiente.
- `baseline_efeito_casa`: baseline com correcao por vies historico especifico de instituto-candidato, com fallback para instituto.
- `baseline_temporal`: baseline com tendencia recente por cenario-candidato, limitado a 5 pontos.
- `bayesiano_dinamico_kalman`: modelo dinamico de estado latente diario por candidato/cenario, estimado por Kalman.
- Machine learning: `ridge`, `elastic_net`, `huber`, `svr_rbf`, `random_forest`, `random_forest_sqrt_600`, `random_forest_07_600`, `extra_trees`, `gradient_boosting`, `ada_boost`.
- Deep learning tabular: `mlp_pequena`, `mlp_media`, `mlp_profunda`.
- IA / ensembles: `voting_ia`, `stacking_ia`.
- `ensemble_ia`: parcial; por enquanto preserva o baseline como previsao principal.

## Referencial teorico

Documento novo: `docs/referencial-teorico.md`. Sete pilares teoricos formais (voto retrospectivo, agregacao de informacao/Condorcet, espaco de estado/Kalman, vies-variancia/ensemble learning, combinacao de previsoes/Bates-Granger, escolha social/Downs-Duverger-Arrow, escore proprio/Brier-Tetlock), cada um amarrado a um modulo especifico de `scripts/`, mais tabela de sintese e secao de delimitacao explicita do que ficou fora e por que.

## Literatura

Documento: `docs/revisao-literatura-metodos.md`. Ampliado em 2026-09-14 com MRP, deep learning/Transformers, redes sociais e sentimento, Google Trends, mercados de previsao, superforecasting, LLMs como simuladores eleitorais, modelagem baseada em agentes, teoria de combinacao de previsoes e paralelos com previsao de conflito armado e epidemias. Adicionada secao "Resultados aplicados" com 4 tabelas comparando MAE/accuracy/Brier score/ganho de ensemble da literatura contra os numeros reais do backtest deste projeto.

Conclusao aplicada ao projeto:

- pesquisas continuam como base principal perto da eleicao;
- fundamentos economicos objetivos ja entram como segunda camada; aprovacao e rejeicao ainda faltam;
- modelos Bayesianos dinamicos sao a evolucao estatistica mais promissora;
- ML, deep learning e IA devem permanecer como desafiantes ate vencerem o baseline fora da amostra.
- a primeira melhoria integrada foi qualidade historica dos institutos, por ser simples, auditavel e comum em agregadores profissionais.
- a segunda melhoria integrada foi incerteza calibrada: os intervalos deixam de ser fixos e a probabilidade de liderar deixa de ser 0/1.
- a terceira melhoria integrada foi efeito casa por instituto-candidato; ela passou a vencer o baseline no backtest geral.
- a quarta melhoria integrada foi o ensemble disciplinado, combinando apenas modelos que vencem ou empatam o baseline puro no backtest geral.
- a quinta melhoria integrada foi fundamentos economicos anuais pre-eleicao vindos do World Bank.
- a sexta melhoria integrada foi o baseline temporal simples; ele venceu os demais baselines na media da previsao viva.
- a setima melhoria integrada foi testar Random Forest com mais arvores e `mtry`/`max_features` alternativo.
- a oitava melhoria integrada foi o modelo Bayesiano dinamico por Kalman; ele entrou no ensemble por vencer o baseline puro no backtest vivo.
- a nona melhoria integrada foi auditoria automatica das fontes historicas e atuais.
- a decima melhoria integrada foi recuperar observacoes auditadas de 1994 e 1998.

## Primeiro backtest

Metodo: deixar uma eleicao historica fora, treinar nas outras e testar no ano segurado.

Erro medio absoluto medio:

- `baseline_pesquisa`: 6,03.
- `baseline_ajustado`: 6,24.
- `baseline_efeito_casa`: 6,43.
- `gradient_boosting`: 6,69.
- `random_forest_07_600`: 6,97.
- `extra_trees`: 7,37.
- `voting_ia`: 16,00.
- `stacking_ia`: 16,15.
- `mlp_pequena`: 17,22.
- `ridge`: 17,58.
- `huber`: 18,52.

Leitura: com 1994, 1998, 2002 e 2006 incorporados, o baseline puro voltou a vencer o backtest geral. O efeito-casa continua util, mas ficou ligeiramente atras do baseline puro.

Observacao sobre fundamentos: PIB, inflacao e desemprego entraram nos modelos supervisionados e no OLS. No backtest atual, eles nao melhoraram o ranking geral dos modelos complexos; ficam mantidos como variaveis explicativas e candidatas para novas rodadas.

Observacao sobre Random Forest: aumentar `n_estimators` para 600 e testar `max_features` melhorou a familia de arvores. A melhor variante atual foi `random_forest_07_600`, com MAE 6,69 contra 7,03 da Random Forest padrao, mas ainda ficou fora do ensemble.

## Ensemble atual

Pesos gerados a partir do primeiro backtest:

- `baseline_pesquisa`: 0,5389.
- `bayesiano_dinamico_kalman`: 0,4611.

Modelos fora do ensemble por enquanto:

- modelos de ML, deep learning e IA que nao venceram o baseline geral.

Motivo: nao venceram o baseline no erro medio absoluto medio apos a limpeza.

## Backtest por janelas

Erro medio absoluto medio por modelo:

- 7 dias antes: 5,71.
- 15 dias antes: 6,21.
- 30 dias antes: 6,93.
- 60 dias antes: 6,89.
- 90 dias antes: 8,46.

Leitura: a direcao geral melhora perto da eleicao, mas a serie ainda nao e monotonicamente limpa porque a base historica tem poucos anos e cenarios heterogeneos.

## Backtest de previsao viva

Este teste simula como o projeto seria usado de verdade: em cada corte, o modelo so enxerga pesquisas ja publicadas ate aquela data.

Erro medio absoluto medio por modelo:

- 7 dias antes: 5,62.
- 15 dias antes: 5,88.
- 30 dias antes: 6,68.
- 60 dias antes: 7,70.
- 90 dias antes: 9,11.

Leitura: este e o teste mais interpretavel ate agora. O baseline temporal simples ainda vence por pouco, mas o Bayesiano dinamico ja fica perto e supera os baselines nao temporais.

## Avaliacao cronologica

Regra:

- Para prever 2010, treinar com 2002 e 2006.
- Para prever 2014, treinar com 2002, 2006 e 2010.
- Para prever 2018, treinar com 2002, 2006, 2010 e 2014.
- Para prever 2022, treinar com 2002, 2006, 2010, 2014 e 2018.
- Para prever 2026, treinar com 2002, 2006, 2010, 2014, 2018 e 2022.

Resultado atual:

- 2010: `random_forest_07_600` venceu com erro medio de 1,34.
- 2014: `voting_ia` venceu com erro medio de 1,69.
- 2018: `baseline_ajustado` venceu empatado com os baselines, com erro medio de 1,92.
- 2022: `voting_ia` venceu com erro medio de 3,58; gradient boosting, Random Forest e Extra Trees tambem ficaram acima do baseline.

Leitura: os modelos de ML ainda oscilam muito entre eleicoes. Devem aparecer no relatorio como comparacao, mas nao devem substituir automaticamente o baseline.

## Previsao gerada

Base usada: pesquisas estruturadas extraidas e normalizadas da Wikipedia, entradas manuais auditadas de 1994/1998, complemento de 2006 em wikitexto, uma pesquisa nacional CESOP/Datafolha de 2002, acervo Fernando Rodrigues/UOL para 2002 e pesquisas recentes de agosto/setembro de 2026, atualizadas ate 24/09/2026.

Cenario principal recente da tabela 2:

- Lula: 42,14% dos votos validos estimados; probabilidade simulada de liderar 70,90%.
- Flavio Bolsonaro: 37,12%; probabilidade simulada de liderar 29,08%.
- Augusto Cury: 7,52%.
- Ronaldo Caiado: 3,44%.
- Romeu Zema: 1,70%.

Cenario principal recente da tabela 2, baseline ajustado:

- Lula: 42,57%; probabilidade simulada de liderar 70,34%.
- Flavio Bolsonaro: 37,65%; probabilidade simulada de liderar 29,64%.

Cenario principal recente da tabela 2, ensemble disciplinado:

- Lula: 42,23%; probabilidade simulada de liderar 72,27%.
- Flavio Bolsonaro: 37,42%; probabilidade simulada de liderar 27,73%.

Cenario recente com Renan Santos, ensemble disciplinado, apos complemento de agosto/setembro:

- Lula: 43,87%; probabilidade simulada de liderar 67,93%.
- Flavio Bolsonaro: 40,45%; probabilidade simulada de liderar 32,07%.
- Renan Santos: 5,23%.
- Augusto Cury: 4,95%.
- Ronaldo Caiado: 2,74%.
- Romeu Zema: 1,16%.

Cenario recente da tabela 4:

- Lula: 44,53% dos votos validos estimados.
- Flavio Bolsonaro: 41,31%.
- Ronaldo Caiado: 3,67%.
- Romeu Zema: 3,31%.

## Importante

Essa previsao inicial serve para testar o fluxo. Ainda nao e uma previsao robusta, porque a base extraida automaticamente precisa de auditoria de qualidade e os cenarios de 2026 ainda precisam de rotulos melhores.

Na rodada de melhoria de 2026-09-12, `avaliar_historico.py` e `avaliar_rolling.py` foram otimizados para usar um catalogo representativo nos backtests e voltaram a recalcular as saidas da base ampliada.

## Proximos passos

1. Expandir 1994 e 1998 com mais pesquisas nacionais, porque hoje ha apenas uma observacao de 1994 e duas de 1998.
2. Validar uma amostra do acervo UOL e das entradas Folha contra PDFs primarios CESOP/Datafolha/Ibope.
3. Melhorar o `bayesiano_dinamico_kalman` com efeito de instituto e fundamentos como prior.
4. Adicionar aprovacao do governo, rejeicao e renda real quando houver serie confiavel.
5. Transformar o backtest vivo em comparacao entre baseline, Bayesiano dinamico e modelos de ML.
