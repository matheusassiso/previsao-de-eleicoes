# Coleta pre-2010

## Incorporado

- 1994: serie consolidada Datafolha de intencao de voto estimulada para presidente, com 15 novas medicoes entre 04-05/04 e 30/09-01/10, inserida em `data/raw/pesquisas_1994_datafolha_serie.csv`. As datas de 23-24/05 e 22/08 ja existiam em entradas manuais auditadas e nao foram duplicadas.
- 1994: uma pesquisa nacional Datafolha publicada pela Folha em 23/08/1994, inserida em `data/raw/pesquisas_1994_1998_folha_manual.csv`.
- 1998: serie consolidada Datafolha de intencao de voto estimulada para presidente, com 8 novas medicoes entre 10-11/03 e 02/10, inserida em `data/raw/pesquisas_1998_datafolha_serie.csv`. As datas de 08-09/07 e 14/08 ja existiam em entradas manuais auditadas e nao foram duplicadas.
- 1998: duas pesquisas nacionais Datafolha publicadas pela Folha em 12/07/1998 e 18/08/1998, inseridas em `data/raw/pesquisas_1994_1998_folha_manual.csv`.
- 2002: uma pesquisa nacional CESOP/Datafolha 01690 de 09/09/2002, com 4.862 entrevistas, inserida em `data/raw/pesquisas_2002_cesop_datafolha.csv`.
- 2002: tabela historica do acervo Fernando Rodrigues/UOL, com 367 linhas por candidato extraidas de 129 pesquisas/cenarios unicos, inserida em `data/raw/pesquisas_2002_uol_fernando_rodrigues.csv`. Como a tabela nao traz amostra linha a linha, as amostras entram imputadas e auditaveis.
- 2006: tres pesquisas de primeiro turno extraidas da pagina em wikitexto da eleicao presidencial de 2006 na Wikipedia em portugues.
- Saida: `data/raw/pesquisas_2006_wikitext.csv`.
- Auditoria especifica: `docs/coleta-2006-wikitext.md`.

## Encontrado, mas ainda nao ingerido

- 2002: artigo de Jairo Nicolau na SciELO usa survey IUPERJ-2002 e regressao logistica para Lula, Serra, Garotinho e Ciro. E util para variaveis explicativas, mas nao e uma serie de pesquisas pre-eleitorais comparavel ao pipeline atual.
- 1994: ainda falta localizar amostras detalhadas para parte das datas da serie consolidada e abrir candidatos menores que aparecem agregados como "outros" no PDF.
- 1998: a serie Datafolha principal foi incorporada. Ainda falta localizar amostras detalhadas para parte das datas e fontes Ibope/CNI comparaveis.

## Fontes consultadas

- 2006 Wikipedia wikitext: https://pt.wikipedia.org/w/index.php?title=Elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2006&action=raw
- 2002 CESOP/Datafolha 01690: https://www.cesop.unicamp.br/vw/1I8v7SqswNQ_MDA_aef91_
- 2002 acervo Fernando Rodrigues/UOL: https://www1.uol.com.br/fernandorodrigues/arquivos/pesquisas/eleicoes2002/pres.shl
- 1994 Folha/Datafolha: https://www1.folha.uol.com.br/fsp/1994/8/23/caderno_especial/1.html
- 1994 Datafolha serie consolidada: https://media.folha.uol.com.br/datafolha/2022/09/01/intencao_de_voto_e_rejeicao_para_presidente_94.pdf
- 1998 Folha/Datafolha julho: https://www1.folha.uol.com.br/fsp/brasil/fc12079807.htm
- 1998 Folha/Datafolha agosto: https://www1.folha.uol.com.br/fsp/brasil/fc18089803.htm
- 1998 Datafolha serie consolidada: https://media.folha.uol.com.br/datafolha/2022/12/28/brasil-1998-1t.pdf
- 2002 SciELO, Jairo Nicolau: https://www.scielo.br/j/bpsr/a/8NVM9Yrsw5VjKnQvYp6J4yR/?lang=en
- 1994 Academia.edu, Datafolha/CESOP citado no artigo: https://www.academia.edu/1444247/Electoral_behaviour_in_Brazil_The_1994_presidential_elections

## Proximo caminho

Prioridade agora e buscar fontes Ibope/CNI para 1994 e 1998 e conferir amostras detalhadas das series consolidadas Datafolha.
