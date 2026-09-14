# Processo e modelo de previsao eleitoral

Objetivo: acompanhar a eleicao presidencial de 2026 no Brasil com previsoes atualizadas conforme novas pesquisas forem adicionadas.

O modelo deve prever o resultado do primeiro turno em votos validos. Ele nao deve "cravar" vencedor; deve produzir estimativas, intervalos e uma trilha historica mostrando como a previsao mudou ao longo do tempo.

## Principio do projeto

Comecar pequeno:

1. CSV com pesquisas.
2. CSV com resultados oficiais.
3. Script que converte pesquisas para votos validos.
4. Baseline de media ponderada.
5. Historico de previsoes salvas por data.

Depois disso, se a base estiver boa, entram modelos mais sofisticados.

## Fontes de dados

### Resultados oficiais

Fonte principal:

- TSE Dados Abertos: https://dadosabertos.tse.jus.br/

Uso:

- baixar resultados oficiais de presidente por ano;
- montar uma tabela de votos validos do primeiro turno por candidato;
- usar essa tabela como alvo historico do modelo.

Eleições desejadas:

- 1994
- 1998
- 2002
- 2006
- 2010
- 2014
- 2018
- 2022

Observacao: se algum ano antigo exigir formato diferente, padronizar manualmente uma vez e manter o CSV limpo em `data/processed/`.

### Pesquisas eleitorais registradas

Fonte principal para pesquisas de 2026:

- PesqEle/TSE: https://pesqele-divulgacao.tse.jus.br/

Uso:

- conferir registro;
- coletar instituto;
- periodo de campo;
- data de divulgacao;
- tamanho da amostra;
- contratante;
- metodologia quando disponivel;
- percentuais por candidato, brancos/nulos e indecisos.

### Pesquisas historicas

Fontes candidatas:

- paginas dos proprios institutos, quando disponiveis;
- arquivos de jornais;
- agregadores e paginas de compilacao, usados apenas como ponto de partida;
- registros oficiais do TSE quando existirem para o ano.

Institutos para mapear:

- Datafolha
- Ibope/Ipec
- Quaest
- AtlasIntel
- PoderData
- CNT/MDA
- Vox Populi
- Sensus
- Ideia
- Paraná Pesquisas

Regra simples: preferir a fonte primaria. Se usar materia jornalistica ou agregador, guardar o link e marcar a confianca como menor.

### Pesquisas atuais de 2026

Noticias recentes indicam levantamentos de institutos como Datafolha, AtlasIntel/Bloomberg, Meio/Ideia, Palver, BTG/Nexus, PoderData/Aya e Quaest. Isso serve para montar a lista inicial de buscas, mas cada pesquisa deve ser checada no PesqEle/TSE ou na fonte primaria antes de entrar como dado definitivo.

Exemplos de fontes de descoberta:

- UOL Eleicoes 2026: https://noticias.uol.com.br/eleicoes/2026/
- Folha Poder: https://www1.folha.uol.com.br/poder/

## Formato da base de pesquisas

Arquivo inicial:

- `data/raw/pesquisas.csv`

Uma linha por candidato dentro de uma pesquisa e cenario.

Campos:

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

Campos que provavelmente entram depois:

- `tipo_pesquisa`: estimulada, espontanea, segundo turno
- `metodo`: presencial, telefone, online, misto
- `contratante`
- `registro_tse`
- `margem_erro`
- `confianca`
- `uf`: sempre BR para nacional, mas deixa o campo se depois quiser estadual

## Padronizacao

Problemas esperados:

- institutos mudam de nome;
- candidatos aparecem com nomes diferentes;
- cenarios incluem ou excluem candidatos;
- pesquisas antigas podem nao informar indecisos do mesmo jeito;
- algumas pesquisas divulgam apenas votos totais, outras ja trazem votos validos.

Tabelas auxiliares futuras:

- `data/processed/institutos.csv`
- `data/processed/candidatos.csv`
- `data/processed/cenarios.csv`

Na primeira versao, evitar tabela demais. Comecar com limpeza direta no script e criar tabelas auxiliares quando a repeticao incomodar.

## Conversao para votos validos

Para cada pesquisa:

```text
base_valida = 100 - brancos_nulos - indecisos
voto_valido_estimado = percentual_total / base_valida * 100
```

Nao forcar os candidatos listados a somarem 100 quando a tabela historica trouxer apenas os principais nomes. Nesses casos, manter o voto valido bruto evita inflar artificialmente os candidatos listados.

Exemplo:

```text
Lula total: 38
Flavio total: 33
Outros totais: 14
Branco/nulo: 8
Indeciso: 7

base_valida = 85
Lula validos = 38 / 85 * 100 = 44,7
Flavio validos = 33 / 85 * 100 = 38,8
```

## Resultado alvo

Arquivo inicial:

- `data/raw/resultados_primeiro_turno.csv`

Campos:

- `ano_eleicao`
- `candidato`
- `percentual_validos`
- `fonte`

O alvo do treinamento sera:

```text
erro = resultado_real_validos - voto_valido_estimado_na_pesquisa
```

## Modelo baseline

A primeira versao deve ser uma media ponderada corrigida por erro historico.

Peso da pesquisa:

```text
peso = peso_recencia * peso_amostra * peso_instituto
```

### Peso por recencia

Pesquisas mais recentes pesam mais.

Ideia inicial:

```text
peso_recencia = exp(-dias_desde_publicacao / meia_vida)
```

Comecar com meia-vida de 21 dias.

### Peso por amostra

Pesquisas maiores pesam um pouco mais, mas sem deixar uma pesquisa enorme dominar tudo.

Ideia inicial:

```text
peso_amostra = sqrt(amostra)
```

### Peso por instituto

No inicio:

```text
peso_instituto = 1
```

Depois, quando houver historico suficiente:

- reduzir peso de instituto com erro historico maior;
- aplicar correcao media de viés por instituto;
- nao corrigir instituto com poucas pesquisas historicas.

## Incerteza

A incerteza deve vir do erro historico por distancia ate a eleicao.

Exemplo:

- pesquisas a 180 dias da eleicao erram mais;
- pesquisas a 30 dias erram menos;
- pesquisas na ultima semana erram menos ainda, mas ainda erram.

Para cada previsao de 2026:

1. calcular dias ate o primeiro turno;
2. buscar erros historicos em janelas parecidas;
3. gerar intervalo por candidato;
4. simular cenarios de primeiro turno.

## Saida do modelo

Cada rodada deve salvar uma previsao datada.

Arquivo futuro:

- `data/processed/previsoes.csv`

Campos:

- `data_previsao`
- `candidato`
- `voto_valido_estimado`
- `intervalo_baixo`
- `intervalo_alto`
- `probabilidade_liderar`
- `probabilidade_ir_ao_segundo_turno`
- `fonte_dados_ate`

Para o primeiro turno, o mais util e:

- estimativa de voto valido por candidato;
- chance de cada candidato terminar em primeiro;
- chance de cada candidato ir ao segundo turno;
- chance de vitoria em primeiro turno, se aplicavel.

## Backtest historico

Antes de confiar na previsao de 2026, testar como o modelo teria se saido no passado.

Processo:

1. escolher uma eleicao passada, por exemplo 2022;
2. esconder o resultado final;
3. usar apenas pesquisas publicadas ate uma data simulada;
4. gerar previsao;
5. comparar com o resultado real;
6. repetir para varias datas antes da eleicao;
7. repetir para 2018, 2014, 2010 etc.

Metricas:

- erro medio absoluto por candidato;
- erro do primeiro colocado;
- acerto dos dois candidatos que foram ao segundo turno;
- calibracao dos intervalos: quantas vezes o resultado real caiu dentro da faixa prevista.

## Ordem pratica de trabalho

1. Preencher resultados oficiais de 1994 a 2022.
2. Coletar algumas pesquisas historicas de 2022 e 2018.
3. Escrever `scripts/preparar_dados.py`.
4. Escrever `scripts/prever.py` com o baseline.
5. Rodar um backtest simples em 2022.
6. So depois ampliar a base para 2014, 2010, 2006, 2002, 1998 e 1994.
7. Inserir pesquisas atuais de 2026.
8. Gerar a primeira previsao viva.

## Decisoes iniciais

- Usar CSV primeiro.
- Nao usar banco de dados agora.
- Nao criar painel web agora.
- Nao usar modelo bayesiano na primeira versao.
- Guardar previsoes antigas para acompanhar mudancas.

## Limites

O numero de eleicoes presidenciais brasileiras comparaveis e pequeno. Isso limita machine learning tradicional. O modelo deve ser interpretavel, com pouca parametrizacao e muita validacao historica.

O maior ganho inicial nao vem de algoritmo sofisticado; vem de uma base limpa e de um backtest honesto.

## Evolucao para modelos mais fortes

Depois do baseline, o projeto pode ter tres familias de modelo rodando em paralelo. A ideia e comparar previsoes, nao escolher um modelo no escuro.

### 1. Modelo inferencial

Objetivo: entender impacto de variaveis explicativas.

Esse modelo responde perguntas como:

- candidatos incumbentes tendem a performar melhor ou pior que as pesquisas?
- sucessores do governo carregam parte do efeito de incumbencia?
- pesquisas online erram diferente de pesquisas presenciais?
- o erro muda conforme a distancia ate a eleicao?
- institutos especificos tem vies historico consistente?

Modelo inicial possivel:

```text
erro_pesquisa ~ dias_ate_eleicao + incumbente + sucessor_governo + metodo + instituto
```

Variavel alvo:

```text
erro_pesquisa = resultado_real_validos - voto_valido_estimado_na_pesquisa
```

Esse modelo nao precisa ser o melhor previsor. Ele serve para explicar quais fatores parecem importar.

### 2. Modelo preditivo tradicional

Objetivo: prever melhor o resultado final.

Modelos candidatos:

- regressao regularizada;
- random forest;
- gradient boosting;
- ensemble simples entre baseline e modelos de arvore.

Entradas:

- voto valido estimado na pesquisa;
- dias ate a eleicao;
- ordem da pesquisa no instituto e cenario;
- ordem da pesquisa na campanha;
- tamanho da amostra;
- instituto;
- metodo da pesquisa;
- volatilidade recente do candidato;
- media movel das ultimas pesquisas;
- tendencia recente;
- dummies estruturais.

Saida:

- percentual final esperado em votos validos;
- intervalo de incerteza;
- probabilidade de liderar;
- probabilidade de ir ao segundo turno.

### 3. Modelo de IA ou rede neural

Objetivo: testar se um modelo mais flexivel captura interacoes que os modelos simples perdem.

So vale depois de existir uma base historica razoavel. Como ha poucas eleicoes presidenciais, o risco de overfitting e alto.

Opcoes realistas:

- rede pequena com poucos atributos;
- modelo sequencial simples para a evolucao das pesquisas;
- ensemble que usa a rede neural como mais um voto, nao como autoridade final.

Regra: se a rede neural nao vencer o baseline em backtest, ela fica fora da previsao principal.

## Variaveis estruturais e dummies

Evitar usar diretamente o nome do candidato como variavel principal do modelo. Nome de candidato pode virar atalho ruim: o modelo aprende "Lula" ou "Bolsonaro" em vez de aprender estrutura eleitoral.

Preferir variaveis como:

- `incumbente`: candidato e o presidente atual;
- `sucessor_governo`: candidato e apoiado pelo presidente atual quando o presidente nao disputa;
- `oposicao_principal`: candidato e o principal opositor ao governo;
- `ex_presidente`: candidato ja foi presidente;
- `governador_estado_grande`: candidato governa ou governou um grande colegio eleitoral;
- `partido_governo`: candidato pertence ao partido do governo federal;
- `reeleicao_permitida`: presidente atual poderia disputar;
- `candidato_governista_sem_incumbente`: caso como 2002, quando FHC nao podia disputar e Serra representava o governo;
- `terceira_via_competitiva`: ha candidato relevante fora dos dois polos principais.
- `dias_campo_ate_eleicao`: dias entre o fim do campo e o primeiro turno;
- `dias_publicacao_ate_eleicao`: dias entre a publicacao e o primeiro turno;
- `ordem_pesquisa_instituto_cenario`: primeira, segunda, terceira etc. para o mesmo instituto e cenario;
- `ordem_pesquisa_campanha`: posicao da pesquisa na sequencia geral da campanha.

Exemplo de leitura:

- 1998: FHC era incumbente.
- 2002: FHC nao podia disputar; Serra era sucessor do governo.
- 2006: Lula era incumbente.
- 2010: Lula nao podia disputar; Dilma era sucessora do governo.
- 2014: Dilma era incumbente.
- 2018: Temer nao era candidato competitivo; eleicao sem incumbente presidencial forte.
- 2022: Bolsonaro era incumbente.
- 2026: classificar conforme o cenario real de candidaturas.

Essas variaveis permitem comparar situacoes parecidas sem fingir que o nome do candidato e uma lei da natureza.

As variaveis de tempo e ordem devem ser derivadas automaticamente, nao preenchidas manualmente. `dias_campo_ate_eleicao` e melhor para explicar erro, porque indica quando a opiniao foi medida. `dias_publicacao_ate_eleicao` e melhor para simular a previsao viva, porque indica quando a pesquisa ficou disponivel para o modelo.

## Ideias para um segundo modelo

Estas variaveis podem melhorar a previsao, mas ficam fora do baseline para evitar complexidade cedo demais:

- `campo_politico`: direita, centro-direita, centro, centro-esquerda, esquerda;
- `alinhamento_governo`: governista, oposicao, independente;
- `polarizacao`: se o candidato pertence a um dos dois polos principais daquela eleicao;
- `transferencia_presidencial`: forca esperada do apoio do presidente a um sucessor;
- `rejeicao`: percentual que declara nao votar no candidato;
- `conhecimento`: percentual que conhece o candidato;
- `aprovacao_governo`: aprovacao do governo federal no periodo da pesquisa;
- `economia`: inflacao, desemprego, renda e crescimento perto da eleicao;
- `evento_relevante`: debate, escandalo, decisao judicial, substituicao de candidato ou choque economico.

Regra para essas variaveis: entram apenas quando houver fonte consistente e backtest mostrando ganho. Ideologia e campo politico podem ajudar, mas tambem podem virar classificacao subjetiva; por isso ficam como camada separada.

## Comparacao entre modelos

Cada modelo deve gerar previsao no mesmo formato:

- candidato;
- voto valido estimado;
- intervalo baixo;
- intervalo alto;
- chance de liderar;
- chance de ir ao segundo turno.

Depois, criar uma tabela comparativa:

- baseline;
- inferencial;
- machine learning;
- IA/rede neural;
- ensemble final.

O ensemble final pode comecar simples:

```text
previsao_final = media ponderada das previsoes dos modelos aprovados no backtest
```

Modelos com backtest ruim recebem peso zero.
