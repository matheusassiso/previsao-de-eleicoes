# Modelo inicial

## Unidade dos dados

Uma linha representa o resultado de um candidato dentro de uma pesquisa, em um cenario especifico.

Campos minimos:

- `ano_eleicao`
- `turno`
- `instituto`
- `data_inicio_campo`
- `data_fim_campo`
- `data_publicacao`
- `amostra`
- `cenario`
- `candidato`
- `percentual_total`
- `brancos_nulos`
- `indecisos`
- `fonte`

Campos derivados:

- `dias_campo_ate_eleicao`
- `dias_publicacao_ate_eleicao`
- `ordem_pesquisa_instituto_cenario`
- `ordem_pesquisa_campanha`

## Conversao para votos validos

Para cada pesquisa:

```text
votos_validos_pesquisa = percentual_total / (100 - brancos_nulos - indecisos)
```

Depois normalizar os candidatos para somarem 100 dentro do mesmo cenario.

Revisao: nao normalizar quando a tabela historica listar apenas parte dos candidatos. Usar o voto valido bruto como medida principal.

## Alvo do treinamento

Comparar `votos_validos_pesquisa` com o percentual real de votos validos do primeiro turno.

O erro pode ser calculado por:

```text
erro = resultado_real_validos - votos_validos_pesquisa
```

## Baseline

Antes de qualquer modelo pesado:

1. media ponderada por recencia;
2. peso por amostra;
3. incerteza baseada no erro historico para a mesma distancia da eleicao;
4. correcao simples por instituto quando o instituto tiver historico suficiente.

## Regra ponytail

Comecar com CSV e script pequeno. Banco de dados, painel web e modelo bayesiano ficam para depois que a base historica estiver limpa.
