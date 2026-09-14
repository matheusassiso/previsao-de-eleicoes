# Coleta recente de 2026

## Incorporado

- BTG/Nexus, divulgado em 08/09/2026: cenario estimulado sem Pablo Marcal, com Lula, Flavio Bolsonaro, Augusto Cury, Ronaldo Caiado, Renan Santos, Romeu Zema, Samara Martins e Rui Costa Pimenta.
- Quaest, divulgado em 07/09/2026: cenario estimulado sem Pablo Marcal, com Lula, Flavio Bolsonaro, Augusto Cury, Renan Santos, Ronaldo Caiado, Romeu Zema e Samara Martins.
- Datafolha, divulgado em 03/09/2026: cenario estimulado com Lula, Flavio Bolsonaro, Augusto Cury, Ronaldo Caiado, Renan Santos e Romeu Zema.
- Futura/Apex, divulgado em 03/09/2026: cenario estimulado com Lula, Flavio Bolsonaro, Augusto Cury, Ronaldo Caiado, Renan Santos, Pablo Marcal, Romeu Zema e candidatos menores. O arquivo incorporado manteve o cenario sem Pablo Marcal para comparabilidade.
- Datafolha, divulgado em 11/09/2026: cenario estimulado com Lula, Flavio Bolsonaro, Augusto Cury, Ronaldo Caiado, Renan Santos, Romeu Zema, Samara Martins, Edmilson Costa, Clariana Barao e Rui Costa Pimenta.
- AtlasIntel/Bloomberg, divulgado em 10/09/2026: cenario estimulado com Pablo Marcal, preservado como cenario alternativo porque a propria fonte informa inelegibilidade.
- PoderData/Aya, divulgado em 10/09/2026: cenario estimulado com Pablo Marcal, Renan Santos e candidatos menores.
- Meio/Ideia, divulgado em 09/09/2026: cenario estimulado com Pablo Marcal, Renan Santos e candidatos menores.
- Palver, divulgado em 09/09/2026: dois cenarios estimulados, com e sem Pablo Marcal; o cenario sem Marcal entrou na previsao principal.
- BTG/Nexus, divulgado em 08/09/2026: cenario com Pablo Marcal incorporado como alternativo; o cenario sem Marcal ja estava na previsao principal.
- Quaest, divulgado em 07/09/2026: cenario com Pablo Marcal incorporado como alternativo; o cenario sem Marcal ja estava na previsao principal.
- AtlasIntel, divulgado em 31/08/2026: cenario estimulado com Pablo Marcal, mantido como alternativo.
- BTG/Nexus, divulgado em 31/08/2026: dois cenarios estimulados, com e sem Pablo Marcal; o cenario sem Marcal entrou na previsao principal.
- PoderData/Aya, divulgado em 27/08/2026: cenario estimulado com Pablo Marcal, mantido como alternativo.

Saida manual auditada: `data/raw/pesquisas_2026_agosto_setembro_manual.csv`.

Tamanho atual: 154 linhas, cobrindo 16 combinacoes de instituto, data de publicacao e cenario. Dessas, 59 linhas estao no cenario principal sem Pablo Marcal e 95 no cenario alternativo com Pablo Marcal.

Auditoria: `data/raw/auditoria_2026_recente.csv`.

Resumo da auditoria em 12/09/2026:

- 6 pesquisas/cenarios com fonte primaria ou quase primaria confirmada: BTG/Nexus nas paginas da Nexus e PoderData/Aya nas paginas do Poder360/PoderData.
- 3 pesquisas/cenarios com registro e metodologia confirmados em fonte forte: AtlasIntel 31/08 via Poder360 e Datafolha de 03/09 e 11/09 via Folha/Datafolha.
- 6 pesquisas/cenarios com registro e metodologia confirmados em fonte secundaria jornalistica: AtlasIntel/Bloomberg, Meio/Ideia, Palver e Quaest.
- 1 pesquisa/cenario Futura/Apex ainda pendente de registro completo aberto no navegador; a biblioteca da Futura indica a rodada, mas a pagina nao expos todos os metadados durante a coleta.

## Observacao

Essas linhas entraram como fonte secundaria/resumo jornalistico. Elas corrigem a ausencia de Renan Santos e candidatos menores na coleta automatica, mas ainda devem ser conferidas contra os PDFs ou paginas oficiais dos institutos quando disponiveis.

O cenario `agosto_setembro_2026_sem_marcal` ficou marcado para previsao principal. O cenario `agosto_setembro_2026_com_marcal` ficou como alternativo, porque as fontes de setembro citam Pablo Marcal como inelegivel.

## Fontes

- Renan Santos nas pesquisas recentes, UOL: https://noticias.uol.com.br/eleicoes/2026/09/08/renan-santos-na-pesquisa-para-presidente-veja-numeros-mais-recentes.ghtm
- Datafolha 11/09/2026, Folha: https://www1.folha.uol.com.br/poder/2026/09/datafolha-lula-tem-39-e-flavio-bolsonaro-35-em-primeiro-turno.shtml
- Quaest 07/09/2026, UOL: https://noticias.uol.com.br/eleicoes/2026/09/07/quaest-presidencial-7-de-setembro.ghtm
- Datafolha 03/09/2026, Folha: https://www1.folha.uol.com.br/poder/2026/09/datafolha-mais-eleitores-viram-conteudo-eleitoral-em-perfis-jornalisticos-nas-redes-sociais.shtml
- Pesquisas recentes de primeiro turno, UOL 11/09/2026: https://noticias.uol.com.br/eleicoes/2026/09/11/pesquisa-presidente-2026-primeiro-turno-veja-numeros-mais-recentes.ghtm
- Pesquisas recentes de primeiro turno, UOL 31/08/2026: https://noticias.uol.com.br/eleicoes/2026/08/31/pesquisa-eleitoral-presidencial-veja-quem-esta-na-frente-dos-ultimos-levantamentos.ghtm
- AtlasIntel 31/08/2026, UOL: https://noticias.uol.com.br/eleicoes/2026/08/31/pesquisa-atlasintel---31-de-agosto.ghtm
- BTG/Nexus 31/08/2026, Nexus: https://www.nexus.fsb.com.br/estudos-divulgados/pesquisa-btg-nexus-de-intencao-de-votos-para-presidente-do-brasil-31-de-agosto-de-2026/
- BTG/Nexus 08/09/2026, Nexus: https://www.nexus.fsb.com.br/estudos-divulgados/pesquisa-btg-nexus-de-intencao-de-votos-para-presidente-do-brasil-8-de-setembro-de-2026/
- PoderData/Aya 27/08/2026, Poder360: https://www.poder360.com.br/poderdata/poderdata-aya-lula-tem-38-contra-35-de-flavio-no-1o-turno/
- PoderData/Aya 10/09/2026, Poder360: https://www.poder360.com.br/poderdata/poderdata-aya-lula-tem-38-contra-36-de-flavio-no-1o-turno/
- AtlasIntel 31/08/2026, Poder360: https://www.poder360.com.br/poder-eleicoes-2026/lula-tem-471-contra-426-de-flavio-no-2o-turno-diz-pesquisa/
