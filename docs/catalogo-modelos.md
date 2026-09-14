# Catalogo de modelos

## Baseline

- `baseline_pesquisa`: media ponderada das pesquisas, sem treino supervisionado.

## Inferencia

- `inferencial_ols`: regressao linear para interpretar relacao entre erro, tempo, amostra e variaveis estruturais.

## Machine learning

- `ridge`
- `elastic_net`
- `huber`
- `svr_rbf`
- `random_forest`
- `random_forest_sqrt_600`: 600 arvores, `max_features="sqrt"` como equivalente de `mtry` reduzido.
- `random_forest_07_600`: 600 arvores, `max_features=0.7`.
- `extra_trees`
- `gradient_boosting`
- `ada_boost`

## Deep learning tabular

Implementado com `MLPRegressor` do scikit-learn para evitar dependencias extras.

- `mlp_pequena`
- `mlp_media`
- `mlp_profunda`

## IA / ensembles

- `voting_ia`
- `stacking_ia`

## Regra de uso

Todos os modelos podem aparecer no relatorio comparativo. Para entrar no ensemble final, o modelo precisa vencer o baseline em validacao fora da amostra.
