# Coleta pre-2010

## Incorporado

- 1994: uma pesquisa nacional Datafolha publicada pela Folha em 23/08/1994, inserida em `data/raw/pesquisas_1994_1998_folha_manual.csv`.
- 1998: duas pesquisas nacionais Datafolha publicadas pela Folha em 12/07/1998 e 18/08/1998, inseridas em `data/raw/pesquisas_1994_1998_folha_manual.csv`.
- 2002: uma pesquisa nacional CESOP/Datafolha 01690 de 09/09/2002, com 4.862 entrevistas, inserida em `data/raw/pesquisas_2002_cesop_datafolha.csv`.
- 2002: tabela historica do acervo Fernando Rodrigues/UOL, com 367 linhas por candidato extraidas de 129 pesquisas/cenarios unicos, inserida em `data/raw/pesquisas_2002_uol_fernando_rodrigues.csv`. Como a tabela nao traz amostra linha a linha, as amostras entram imputadas e auditaveis.
- 2006: tres pesquisas de primeiro turno extraidas da pagina em wikitexto da eleicao presidencial de 2006 na Wikipedia em portugues.
- Saida: `data/raw/pesquisas_2006_wikitext.csv`.
- Auditoria especifica: `docs/coleta-2006-wikitext.md`.

## Encontrado, mas ainda nao ingerido

- 2002: artigo de Jairo Nicolau na SciELO usa survey IUPERJ-2002 e regressao logistica para Lula, Serra, Garotinho e Ciro. E util para variaveis explicativas, mas nao e uma serie de pesquisas pre-eleitorais comparavel ao pipeline atual.
- 1994: ainda falta uma serie completa. O artigo hospedado na Academia.edu referencia serie Datafolha/CESOP com amostras de maio a setembro, mas a pagina aberta nao trouxe percentuais completos em texto extraivel.
- 1998: ainda falta uma serie completa. As duas entradas atuais vieram de noticias da Folha; nao de tabela consolidada de instituto.

## Fontes consultadas

- 2006 Wikipedia wikitext: https://pt.wikipedia.org/w/index.php?title=Elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2006&action=raw
- 2002 CESOP/Datafolha 01690: https://www.cesop.unicamp.br/vw/1I8v7SqswNQ_MDA_aef91_
- 2002 acervo Fernando Rodrigues/UOL: https://www1.uol.com.br/fernandorodrigues/arquivos/pesquisas/eleicoes2002/pres.shl
- 1994 Folha/Datafolha: https://www1.folha.uol.com.br/fsp/1994/8/23/caderno_especial/1.html
- 1998 Folha/Datafolha julho: https://www1.folha.uol.com.br/fsp/brasil/fc12079807.htm
- 1998 Folha/Datafolha agosto: https://www1.folha.uol.com.br/fsp/brasil/fc18089803.htm
- 2002 SciELO, Jairo Nicolau: https://www.scielo.br/j/bpsr/a/8NVM9Yrsw5VjKnQvYp6J4yR/?lang=en
- 1994 Academia.edu, Datafolha/CESOP citado no artigo: https://www.academia.edu/1444247/Electoral_behaviour_in_Brazil_The_1994_presidential_elections

## Proximo caminho

Prioridade agora e buscar acesso direto ao Banco de Dados Datafolha/CESOP ou aos acervos dos institutos. Sem percentuais completos por candidato, essas eleicoes devem ficar fora do treino de pesquisas para nao gerar observacoes artificiais.
