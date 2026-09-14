# Avaliacao cronologica dos modelos

Objetivo: avaliar os modelos do jeito correto para uma previsao eleitoral real.

## Regra

Para prever uma eleicao, o modelo so pode treinar com eleicoes anteriores.

- Previsao de 2010: treino com 2006.
- Previsao de 2014: treino com 2006 e 2010.
- Previsao de 2018: treino com 2006, 2010 e 2014.
- Previsao de 2022: treino com 2006, 2010, 2014 e 2018.
- Previsao de 2026: treino com 2006, 2010, 2014, 2018 e 2022.

## Modelos comparados

- `baseline_pesquisa`: media ponderada das pesquisas recentes.
- `inferencial_ols`: regressao linear interpretavel.
- `ridge`: regressao regularizada.
- `elastic_net`: regressao regularizada combinando L1 e L2.
- `huber`: regressao robusta contra outliers.
- `svr_rbf`: regressao de vetor de suporte com kernel RBF.
- `random_forest`: modelo de arvore em ensemble.
- `extra_trees`: ensemble de arvores extremamente aleatorizadas.
- `gradient_boosting`: boosting de arvores.
- `ada_boost`: boosting simples.
- `mlp_pequena`, `mlp_media`, `mlp_profunda`: redes neurais tabulares.
- `voting_ia`, `stacking_ia`: ensembles de IA.

## Resultado atual

Erro medio absoluto:

- 2010: baseline venceu com erro medio de 3,39 pontos.
- 2014: `mlp_media` venceu com erro medio de 0,62 ponto, mas com treino ainda pequeno.
- 2018: baseline venceu com erro medio de 1,92 ponto.
- 2022: huber venceu com erro medio de 4,41 pontos; baseline ficou com 6,99.

## Leitura

O baseline continua sendo o ponto de referencia principal. Os modelos mais fortes ainda oscilam muito porque ha poucos ciclos eleitorais historicos e as tabelas extraidas automaticamente sao heterogeneas.

O modelo final de 2026 deve mostrar todos os modelos, mas destacar o baseline e tratar ML/deep learning como cenarios auxiliares ate vencerem em validacao mais robusta.
