# Revisao de literatura: metodos para prever eleicoes e eventos similares

Atualizado em 2026-09-14 com uma rodada ampliada de pesquisa bibliografica, cobrindo metodos classicos, machine learning, deep learning, IA generativa e familias de modelos usadas para eventos correlatos (conflitos, epidemias). Mantem a sintese e as conclusoes praticas da versao anterior e adiciona novas familias de metodos, casos internacionais e uma lista de referencias muito mais ampla.

## Sintese executiva

A literatura de previsao eleitoral converge para uma regra pratica: pesquisas sao a informacao mais forte perto da eleicao, mas fundamentos politicos e economicos ajudam quando a eleicao ainda esta distante. Modelos profissionais combinam essas duas fontes, corrigem vies historico de institutos, tratam a incerteza explicitamente e avaliam tudo por backtest cronologico. A pesquisa ampliada confirma esse nucleo e acrescenta quatro conclusoes novas relevantes para este projeto:

1. **MRP (multilevel regression and poststratification)** virou o padrao de fato para previsao subnacional (estado, distrito, regiao) a partir de poucas pesquisas nacionais grandes, e e hoje usado tanto nos EUA quanto na Alemanha e no Reino Unido. E o proximo passo natural se o projeto quiser desagregar por regiao brasileira.
2. **Combinacao de previsoes tem um "puzzle" bem documentado**: a media simples entre modelos frequentemente empata ou supera esquemas de peso sofisticados, porque a matriz de covariancia dos erros e dificil de estimar com poucos dados. Isso reforca a escolha atual do projeto de um ensemble disciplinado e conservador em vez de otimizar pesos livremente.
3. **Redes sociais e busca (Twitter/X, Google Trends) tem historico misto**: o resultado inicial mais citado (Tumasjan et al., 2010) foi replicado com sucesso parcial e depois contestado por replicacoes com taxa de acerto proxima do acaso. A leitura correta e usar essas fontes como sinal fraco complementar, nunca como substituto de pesquisa.
4. **Grandes modelos de linguagem (LLMs)** comecaram a ser testados como simuladores de eleicao em 2024-2026, com resultados promissores em direcao do vencedor, mas vies sistematico documentado (superestimam um dos campos politicos). Interessante como desafiante experimental, nao como modelo principal.

Para o projeto de previsao presidencial brasileira de 2026, a estrategia mais defensavel continua:

1. manter um baseline de pesquisas como previsao principal;
2. usar modelos inferenciais para entender erro, incumbencia e distancia ate a eleicao;
3. usar ML, redes neurais, LLMs e ensembles como modelos desafiantes;
4. so promover modelos complexos para a previsao principal se vencerem o baseline fora da amostra, com peso proximo da media simples entre os aprovados (nao pesos livremente otimizados).

## Integrado nesta rodada (historico do projeto)

Foram integradas quatro melhorias de eficiencia usadas por agregadores profissionais:

- limpeza de marcadores de referencia nos nomes dos institutos, para consolidar historico de erro;
- tabela `qualidade_institutos.csv`, com linhas historicas, vies medio e erro medio absoluto por instituto;
- `baseline_ajustado`, que corrige a intencao de voto pelo vies medio do instituto quando ha amostra historica suficiente;
- `baseline_efeito_casa`, que usa vies historico especifico de instituto-candidato quando ha amostra suficiente;
- intervalos e probabilidades simuladas calibrados pelo erro historico medio de cada modelo;
- `ensemble_disciplinado`, que combina apenas modelos aprovados pelo backtest geral;
- fundamentos economicos anuais pre-eleicao: crescimento real do PIB, inflacao e desemprego;
- `baseline_temporal`, uma aproximacao simples de modelo dinamico que projeta tendencia recente com teto de 5 pontos;
- `bayesiano_dinamico_kalman`, um modelo de estado latente diario estimado por filtro de Kalman.

Com a base ampliada (1994-2026), o `baseline_pesquisa` puro voltou a vencer o backtest geral por leave-one-year-out (MAE 6,03 contra 6,43 do `baseline_efeito_casa`), mas o efeito-casa continua vencendo na previsao viva (7,47 contra 7,66). O ensemble combina `baseline_efeito_casa` e `bayesiano_dinamico_kalman`, preservando o baseline puro como ancora, e gera a saida `previsao_ensemble.csv`. Ver numeros completos e comparacao com a literatura na secao "Resultados aplicados" abaixo.

## Familias de modelos (visao geral)

| Familia | Ideia central | Forca | Risco | Uso no projeto |
|---|---|---|---|---|
| Media de pesquisas | Combinar pesquisas recentes, ponderando por recencia, amostra e qualidade | Forte perto da eleicao; simples de auditar | Herda vies sistematico das pesquisas | `baseline_pesquisa`, `baseline_ajustado`, `baseline_efeito_casa` |
| Fundamentos | Usar economia, aprovacao, incumbencia e tempo no poder | Util antes das pesquisas estabilizarem | Pode importar relacoes de outro pais/contexto | Proxima camada de variaveis |
| MRP | Regressao multinivel + poststratificacao para desagregar por regiao/subgrupo | Produz estimativa subnacional a partir de uma pesquisa nacional grande | Exige poststrata censitarios confiaveis e boa especificacao do modelo multinivel | Nao implementado; candidato para desagregacao regional |
| Inferencia | Regressao explicavel para erro ou voto final | Interpreta impactos e incerteza | Linearidade e pouca amostra | `inferencial_ols` |
| ML tabular | Aprender relacoes nao lineares em dados historicos | Pode capturar interacoes | Overfitting com poucas eleicoes | Ridge, Elastic Net, Huber, SVR, arvores, boosting |
| Deep learning / Transformers | Redes neurais e atencao sobre series temporais de pesquisas | Flexivel, capta padroes complexos | Faminto por dados; poucas eleicoes historicas | MLP pequena/media/profunda; Transformer nao implementado |
| Bayesiano dinamico | Estado latente da corrida evolui no tempo | Bom para nowcast vivo e incerteza | Mais complexo de implementar e validar | `bayesiano_dinamico_kalman` e `baseline_temporal` |
| Texto e redes sociais | Sentimento e volume de mencoes em redes | Dado de alta frequencia, barato de coletar | Ruidoso, manipulavel (bots), historico de acerto fraco | Nao implementado |
| Big data / buscas | Volume de busca (Google Trends) como proxy de interesse/intencao | Alta frequencia, cobre pessoas que nao respondem pesquisa | Amostra do Google e parcial e muda com o tempo; risco de correlacao espuria | Nao implementado |
| Mercados de previsao | Precos de apostas agregam informacao dispersa | Historicamente competitivo com pesquisas, as vezes melhor a mais de 100 dias da eleicao | Liquidez baixa, exposto a manipulacao e vies de quem aposta | Nao implementado |
| Julgamento humano agregado (superforecasting) | Combinar previsores humanos calibrados e treinados em base rate | Bom para horizontes de meses; incorpora contexto qualitativo dificil de codificar | Caro de operar; nao escala automaticamente | Nao implementado |
| LLMs / IA generativa | Simular eleitores ou pedir previsao direta a um modelo de linguagem | Barato de rodar, incorpora conhecimento textual amplo | Vies sistematico documentado; dificil de auditar | Nao implementado; candidato experimental |
| Modelagem baseada em agentes (ABM) | Simular decisao individual de eleitores e agregar | Nao depende de pesquisa; interpretavel por bloco de eleitor | Exige calibracao cuidadosa de regras comportamentais | Nao implementado |
| Ensembles | Combinar modelos independentes | Geralmente melhora estabilidade | Pode esconder erro se modelos ruins entram; puzzle da combinacao | `voting_ia`, `stacking_ia`, ensemble com pesos |

## Modelos baseados em pesquisas

Modelos de media de pesquisas sao o ponto de partida mais comum em previsao eleitoral moderna. A logica e simples: cada pesquisa observa a intencao de voto com erro amostral e erro nao amostral; combinar pesquisas reduz parte do ruido. Modelos profissionais acrescentam ponderacoes por tamanho da amostra, recencia, modo de coleta, historico do instituto e efeitos de casa.

O legado do FiveThirtyEight popularizou esse desenho: agregacao de pesquisas, avaliacao de institutos, ajuste por efeitos de casa e transformacao da media em distribuicoes probabilisticas. Modelos do tipo `polls-only` evitam fundamentos e tentam responder "se a eleicao fosse hoje"; modelos `polls-plus` adicionam informacoes estruturais para antecipar movimento futuro. O modelo do The Economist para 2020 e 2024 segue a mesma familia, combinando pesquisas estaduais e nacionais com fundamentos economicos num modelo Bayesiano dinamico (ver secao seguinte).

No projeto, o `baseline_pesquisa` segue essa tradicao em versao curta: usa pesquisa recente, amostra e recencia. Ele deve continuar sendo o adversario minimo de qualquer modelo mais sofisticado.

Melhorias naturais:

- peso por erro historico do instituto;
- ajuste por metodo de coleta;
- efeito de casa por instituto;
- suavizacao temporal por candidato;
- tratamento separado de pesquisas muito antigas e muito recentes;
- intervalos probabilisticos calibrados por erro historico.

## Fundamentos politicos e economicos

Modelos de fundamentos partem da ideia de voto retrospectivo: eleitores recompensam ou punem o grupo no poder conforme desempenho economico, aprovacao presidencial e fadiga com o partido incumbente. Abramowitz, no modelo Time-for-Change, usa crescimento economico, aprovacao presidencial e tempo do partido na Casa Branca. Hibbs, no Bread and Peace, enfatiza crescimento real de renda e custos politicos de guerras.

Erikson e Wlezien, em *The Timeline of Presidential Elections* (2012), usam quase duas mil pesquisas nacionais de 1952 a 2008 para mostrar que pesquisas do inicio do ano quase nao tem poder preditivo, mas por volta de abril, quando os candidatos ja estao definidos, a preferencia declarada acerta o vencedor em 11 das 15 eleicoes analisadas. A conclusao central do livro e que "fundamentos importam, mas apenas porque as campanhas os revelam" — ou seja, fundamentos e campanha nao sao explicacoes rivais, sao complementares: a campanha e o mecanismo pelo qual o eleitor toma conhecimento dos fundamentos.

Para o Brasil, as variaveis equivalentes mais objetivas seriam:

- incumbente candidato a reeleicao;
- sucessor governista quando o presidente nao disputa;
- tempo do campo governista no poder;
- aprovacao do governo;
- inflacao acumulada;
- desemprego;
- crescimento do PIB;
- renda real;
- percepcao economica nas pesquisas;
- rejeicao dos candidatos.

Essas variaveis devem entrar com cuidado. A literatura dos EUA nao transfere automaticamente para o Brasil porque o sistema partidario, a volatilidade, a fragmentacao e o desenho multipartidario sao diferentes. Ainda assim, incumbencia, economia e aprovacao sao suficientemente objetivas para uma segunda camada.

## MRP: regressao multinivel com poststratificacao

MRP (multilevel regression and poststratification) e hoje a tecnica dominante para transformar uma unica pesquisa nacional grande em estimativas confiaveis por estado, distrito ou subgrupo demografico. A ideia foi introduzida por Gelman e Little (1997) e tem dois passos: (1) ajustar uma regressao multinivel (hierarquica, geralmente Bayesiana) da intencao de voto usando muitas covariaveis demograficas e geograficas, regularizando grupos com poucas observacoes; (2) poststratificar, isto e, reponderar as previsoes de cada celula demografica pelo peso real dessa celula na populacao (censo ou projecao censitaria), corrigindo o desbalanceamento da amostra.

Wang, Rothschild, Goel e Gelman (2015), em "Forecasting elections with non-representative polls" (o "estudo do Xbox"), mostraram que MRP consegue corrigir uma amostra fortemente nao representativa (jogadores de Xbox, majoritariamente homens jovens) e ainda assim recuperar estimativas competitivas com pesquisas tradicionais na eleicao americana de 2012. Ghitza e Gelman (2013), em "Deep Interactions with MRP", aprofundam a tecnica para capturar interacoes profundas entre subgrupos (por exemplo, raca x idade x estado) na previsao de turnout e escolha de voto. Isakov e Kuriwaki, em "Predicting State Presidential Election Results Using National Tracking Polls and MRP" (Public Opinion Quarterly, 2020), aplicam a tecnica para gerar previsoes estaduais a partir apenas de pesquisas de rastreamento nacional.

Desde meados dos anos 2010, MRP passou a ser adotado por institutos comerciais e academicos, com destaque para o Reino Unido (a YouGov usou MRP para acertar a perda da maioria conservadora em 2017) e, mais recentemente, a Alemanha: a YouGov publicou um modelo MRP para a eleicao federal alema de 2025, e o projeto academico Zweitstimme (Hertie School, Universidade de Mannheim e Universidade de Witten/Herdecke) combina um modelo fundamentalista com pesquisas num modelo Bayesiano dinamico para gerar previsoes de coalizao e de cadeiras vagas.

Relevancia para o projeto: o Brasil tem poucas pesquisas com amostra grande o bastante para MRP subnacional hoje, mas a tecnica e o candidato natural caso o projeto queira desagregar previsao por regiao, estado ou faixa de renda no futuro, especialmente se pesquisas com microdados de respondente (nao so agregados) ficarem disponiveis.

## Modelos inferenciais

Regressoes lineares e generalizadas sao uteis porque explicam, nao apenas preveem. Um modelo inferencial pode estimar se pesquisas distantes erram mais, se candidatos incumbentes tem erro medio diferente, se determinados institutos tendem a superestimar ou subestimar candidatos, e se brancos/nulos/indecisos alteram a conversao para votos validos.

No projeto, o `inferencial_ols` e a versao inicial. Ele usa `voto_valido_estimado`, dias ate a eleicao, amostra e dummies politicas. O papel dele nao e necessariamente vencer em previsao; e mostrar o que o modelo esta usando e onde pode haver vies.

Proxima versao recomendada:

- trocar OLS simples por regressao hierarquica com efeitos de instituto;
- prever erro da pesquisa em vez de prever voto final diretamente;
- separar efeito de ano eleitoral, instituto e candidato;
- calibrar intervalo de incerteza com residuos historicos.

## Modelos Bayesianos dinamicos

Modelos Bayesianos dinamicos tratam a intencao de voto como um estado latente que muda ao longo da campanha. Pesquisas sao observacoes imperfeitas desse estado. Esse desenho e especialmente forte para previsao viva, porque consegue combinar informacao nova com uma trajetoria temporal e produzir incerteza coerente.

Linzer propoe um modelo Bayesiano dinamico para eleicoes presidenciais americanas com pesquisas estaduais. Heidemanns, Gelman e Morris atualizam esse tipo de abordagem em um modelo que combina pesquisas, fundamentos e simulacoes (a base do modelo do The Economist). Stoetzer e coautores adaptam a familia Bayesiana para sistemas multipartidarios em "Forecasting Elections in Multiparty Systems: A Bayesian Approach Combining Polls and Fundamentals" (Political Analysis, 2019), o que interessa mais ao Brasil. O projeto Zweitstimme para a Alemanha usa o mesmo principio: um modelo fundamentalista entra como prior no dia da eleicao e vai sendo atualizado por pesquisas ao longo da campanha, com saida em forma de probabilidade de cada coalizao alcancar maioria.

Para sistemas multipartidarios, uma alternativa complementar e a regressao de Dirichlet, adequada porque as fracoes de voto de todos os partidos precisam somar 100%; ela aparece em "Forecasting multiparty by-elections using Dirichlet regression" e em "Picking the winner(s): Forecasting elections in multiparty systems", ambos explorando como prever simultaneamente a chance de coalizoes atingirem maioria e partidos pequenos ultrapassarem clausula de barreira.

Para o nosso projeto, a familia Bayesiana dinamica e a versao estatistica mais promissora depois do baseline. A primeira implementacao usa um modelo linear-gaussiano de estado latente com filtro de Kalman:

- estima tendencia diaria por candidato;
- separa ruido de pesquisa de mudanca estimada da opiniao;
- gera intervalos por candidato e simulacoes de lideranca/segundo turno;
- roda com a base atual sem depender de PyMC, Stan ou MCMC.

O backtest vivo inicial deixa esse modelo perto do `baseline_temporal` e acima dos baselines nao temporais. Por isso, ele entrou no `ensemble_disciplinado` com peso condicionado ao backtest vivo. A proxima evolucao natural e usar fundamentos como prior e efeitos hierarquicos de instituto, seguindo o desenho do Zweitstimme.

## Machine learning tabular

ML tabular tenta aprender relacoes entre caracteristicas da pesquisa e resultado final. No projeto, os modelos usados foram:

- `ridge`: regressao linear regularizada com penalizacao L2;
- `elastic_net`: regularizacao combinando L1 e L2;
- `huber`: regressao robusta contra outliers;
- `svr_rbf`: regressao de vetor de suporte com kernel radial;
- `random_forest` / `random_forest_sqrt_600` / `random_forest_07_600`: ensemble de arvores, com variantes de numero de arvores e `max_features`;
- `extra_trees`: arvores extremamente aleatorizadas;
- `gradient_boosting`: boosting sequencial de arvores;
- `ada_boost`: boosting adaptativo.

A literatura recente de 2024-2026 reforca esse desenho: um estudo do Munich Personal RePEc Archive usa lasso, random forest e gradient boosting para prever a fatia de votos do partido do governo na eleicao americana de 2024, com o lasso como estimativa mais consistente. Outro estudo (2018, eleicao do Senado no Texas) combina random forest e gradient boosting com resultados historicos de 2008-2016, pesquisas granulares e peso relativo de temas de campanha, acertando a fatia de votos de Ted Cruz com erro de apenas 0,89 ponto percentual. Um terceiro artigo, "Forecasting political voting: A high dimensional machine learning approach" (ScienceDirect), testa ML de alta dimensionalidade especificamente para previsao de voto. A leitura consistente entre esses trabalhos e que **metodos de ensemble de arvores (gradient boosting e random forest) tendem a liderar entre os modelos de ML tabular** quando ha engenharia de atributos cuidadosa, mas ainda dependem de volume de dados historicos que eleicoes presidenciais isoladas raramente oferecem.

Eles fazem sentido como desafiantes do baseline. A vantagem e capturar interacoes: por exemplo, o efeito de uma pesquisa de 90 dias antes pode depender do instituto, do tamanho da amostra e do candidato ser incumbente. O risco e grande porque o numero de eleicoes presidenciais brasileiras observadas e pequeno. Muitas linhas no CSV nao significam muitas eleicoes independentes; linhas da mesma campanha sao correlacionadas.

Leitura do backtest atual do projeto:

- `baseline_pesquisa`: MAE medio 6,40 (backtest geral simples) / 6,03 (apos base ampliada);
- `svr_rbf`: MAE medio 6,58;
- `elastic_net`: MAE medio 8,29;
- `ridge`: MAE medio 8,79;
- `gradient_boosting`: 6,69; `random_forest_07_600`: 6,97; `extra_trees`: 7,37 (apos base ampliada, backtest cronologico leave-one-year-out);
- ML venceu em alguns anos (2010, 2022 com variantes de arvore ou `voting_ia`), mas ainda nao de forma consistente entre eleicoes.

Conclusao: manter ML no relatorio comparativo; nao usar automaticamente como previsao principal ate vencer em backtest cronologico e em previsao viva de forma consistente.

## Deep learning e Transformers

Redes neurais tabulares podem aproximar relacoes complexas, mas sao famintas por dados. Em eleicoes presidenciais, o problema real e pequeno: ha poucas eleicoes independentes, mudancas institucionais relevantes e cenarios de candidatos diferentes. Por isso, redes MLP e arquiteturas mais recentes devem ser tratadas como experimento controlado.

No projeto, foram usados:

- `mlp_pequena`, `mlp_media`, `mlp_profunda`: redes MLP com 1, 2 e 3 camadas ocultas;
- `voting_ia`, `stacking_ia`: ensembles de IA combinando arvores e boosting.

O melhor sinal ate agora foi pontual: `mlp_media` venceu em 2014 no rolling backtest, mas isso e fragil porque o treino vinha basicamente de 2006 e 2010. A leitura correta e nao "a rede neural e melhor"; e "redes podem ajustar bem casos especificos, mas ainda precisam provar estabilidade".

Fora do projeto, a literatura de deep learning para series temporais avancou muito nos ultimos anos. Revisoes recentes (survey de transformers para forecasting, ScienceDirect 2025-2026; "A Survey of Deep Learning for Time Series Forecasting", arXiv 2503.10198) documentam a evolucao de CNNs e RNNs/LSTM para arquiteturas baseadas em atencao (Transformer), que capturam dependencias de longo prazo com mais eficiencia computacional que LSTM em series longas e de alta dimensionalidade. Especificamente para pesquisas eleitorais, um artigo de 2026 ("A Hybrid Transformer-Ensemble Framework for Precise Election Poll Analysis", journal Computers) combina atencao de Transformer com ensembles de Random Forest, XGBoost e Gradient Boosting, comparando sistematicamente contra LSTM, GRU e CNN temporal como baselines — um desenho de "IA hibrida" que converge com a conclusao geral desta revisao: IA generativa/profunda funciona melhor como componente de um ensemble disciplinado do que isolada.

O uso mais defensavel de IA aqui nao e uma rede profunda isolada. E um ensemble disciplinado:

- incluir apenas modelos que vencem o baseline fora da amostra;
- ponderar por desempenho recente e historico (evitando otimizar pesos livremente — ver secao sobre combinacao de previsoes);
- manter baseline como ancora;
- reportar dispersao entre modelos como indicador de incerteza;
- bloquear modelos com previsoes absurdas ou instaveis.

Se o projeto quiser experimentar deep learning de forma mais seria no futuro, a sequencia recomendada pela literatura e: (1) uma rede recorrente simples (LSTM/GRU) sobre a serie diaria de pesquisas por candidato, comparada diretamente contra o `bayesiano_dinamico_kalman`; (2) so escalar para Transformer se o LSTM mostrar ganho consistente, porque Transformer exige mais dado e mais cuidado de regularizacao para nao overfitar com poucas eleicoes historicas.

## Texto, redes sociais e sentimento

Usar volume e sentimento de mencoes em redes sociais para prever eleicoes e uma linha de pesquisa influente, mas com historico de replicacao problematico — vale registrar isso explicitamente para nao repetir erros ja documentados.

Tumasjan, Sprenger, Sandner e Welpe (2010), em "Predicting Elections with Twitter: What 140 Characters Reveal About Political Sentiment", analisaram cerca de 100 mil tweets sobre a eleicao alema de 2009 e reportaram que a proporcao de mencoes a partidos e politicos se aproximava do resultado real, quase tao bem quanto pesquisas tradicionais, usando o dicionario LIWC para analise semantica. O resultado gerou grande repercussao, mas Gayo-Avello e coautores testaram o mesmo metodo em eleicoes americanas (Senado de Massachusetts, eleicoes legislativas) e encontraram acerto em apenas parte dos casos; revisoes posteriores relatam taxas de acerto entre 50% e 63%, proximas do acaso. Um artigo de sintese posterior, "Stop trying to predict elections only with twitter – There are other data sources and technical issues to be improved" (ScienceDirect), formaliza essa critica e recomenda tratar redes sociais como uma fonte entre varias, nunca isolada.

Aplicacoes mais recentes continuam a linha, com resultados mistos: analise de intencao de voto a partir de conteudo do Twitter no Reino Unido em 2010; sentimento de tweets e caracteristicas socioeconomicas regionais na eleicao parlamentar polonesa de 2019; e, mais proximo do estado da arte, "A Hybrid Method of Sentiment Analysis and Machine Learning Algorithm for the U.S. Presidential Election Forecasting" (arXiv 2312.05584) e um estudo sobre a eleicao presidencial turca de 2023 usando dados de redes sociais combinados com ML.

Leitura para o projeto: redes sociais nao sao um substituto de pesquisa, mas podem funcionar como sinal de alta frequencia para nowcasting entre pesquisas, contanto que o modelo trate esse sinal com peso baixo e sujeito a auditoria (deteccao de bots, coordenacao artificial, e vies de quem usa a rede vs. quem vota).

## Big data e Google Trends

Volume de busca no Google e outra fonte de alta frequencia usada para tentar antecipar movimento de opiniao entre pesquisas. Estudos como "Using Search Query Data to Predict the General Election: Can Google Trends Help" e "Revolutionizing Election Forecasts: Google Trends and Big Data Analytics in U.S. Presidential Predictions" argumentam que volume de busca por candidato captura interesse publico sem o vies de desejabilidade social presente em pesquisas declaradas. Um estudo mais cetico, "Can we predict multi-party elections with Google Trends data? Evidence across elections, data windows and model classes", testa a tecnica sistematicamente em varias eleicoes multipartidarias e varias janelas de tempo, encontrando desempenho inconsistente entre paises e periodos.

As limitacoes documentadas sao relevantes: o Google Trends usa apenas uma amostra aleatoria pequena das buscas, com defasagem de ate 36 horas; o algoritmo de busca muda com o tempo, o que contamina comparacoes historicas; e correlacoes especificas de uma eleicao raramente generalizam para outra. Tratamento recomendado: usar como variavel explicativa auxiliar num modelo maior (nunca como previsor unico), sempre normalizando pela mesma janela de coleta.

## Mercados de previsao (prediction markets)

Mercados de apostas politicas agregam informacao dispersa atraves do preco: cada participante aposta com dinheiro proprio baseado no que acredita saber, e o preco de equilibrio reflete a probabilidade implicita coletiva. Os Iowa Electronic Markets (IEM), operando desde 1988, sao o caso mais estudado: comparando previsoes do IEM com 964 pesquisas ao longo de cinco eleicoes presidenciais americanas (1988-2004), os precos do mercado ficaram mais proximos do resultado final que a pesquisa em 74% dos casos, com erro medio de 1,5 ponto percentual na semana anterior a eleicao contra 2,1 pontos do ultimo Gallup. Wolfers e Zitzewitz (2004), num working paper do NBER que se tornou referencia, revisam a teoria e evidencia empirica de mercados de previsao em dominios variados (eleicoes, vendas, eventos macroeconomicos, bilheteria de cinema), destacando que mercados tendem a superar pesquisas especialmente com mais de 100 dias de antecedencia da eleicao. Um estudo mais recente (2025, "Are Betting Markets Better than Polling in Predicting Political Elections?") revisita a comparacao com dados atuais.

Limitacoes praticas: liquidez baixa em mercados menores gera precos ruidosos; participantes podem ter vieses coletivos (ex. excesso de otimismo de um lado politico); e em alguns paises mercados de apostas politicas sao regulados ou proibidos, o que limita a leitura para o Brasil, onde nao ha um mercado de apostas eleitorais liquido e legal comparavel ao IEM ou PredictIt.

## Superforecasting e julgamento humano agregado

Philip Tetlock e Barbara Mellers lideraram o Good Judgment Project (GJP), reunindo milhares de voluntarios para responder perguntas de torneios geopoliticos financiados pela IARPA (2011-2015). Os melhores previsores amadores — os "superforecasters" — superaram analistas de inteligencia profissionais com acesso a informacao classificada em cerca de 30%. O metodo central de Tetlock foi pontuar as previsoes como meteorologistas pontuam previsao do tempo (Brier score) e treinar os participantes a melhorar iterativamente. Pesquisa subsequente sobre as justificativas escritas pelos melhores previsores identificou padroes cognitivos distintivos, como "complexidade dialetica" (tolerancia a perspectivas conflitantes e capacidade de sintetiza-las) e uso sistematico de taxas-base (base rates) como ancora antes de ajustar para especificidades do caso. Um algoritmo de agregacao desenvolvido durante os torneios superou 99,8% dos previsores individuais que compunham a media. O proprio Tetlock recomenda essa abordagem para horizontes de 3 a 18 meses — mais curto que uma corrida presidencial completa, mas compativel com a janela final de campanha.

O livro *Superforecasting: The Art and Science of Prediction* (Tetlock e Gardner, 2015) e a referencia de divulgacao mais citada desse programa de pesquisa.

Relevancia para o projeto: um comite de previsores humanos treinados nao substitui o pipeline quantitativo, mas o principio de "pontuar e recalibrar" e diretamente aplicavel — o projeto ja faz isso ao calibrar intervalos pelo erro historico de cada modelo, que e essencialmente um Brier/CRPS informal.

## Modelos de linguagem (LLMs) como simuladores eleitorais

A partir de 2024, uma leva de artigos comecou a testar grandes modelos de linguagem (GPT-4o e similares) como simuladores diretos de eleicao, seja pedindo a previsao diretamente, seja simulando "personas" de eleitores individuais e agregando as respostas.

"Using Large Language Models to Forecast the 2024 U.S. Presidential Election: Accuracy, Bias, and Media Influence" usa GPT-4o como simulador preditivo, encontrando forte alinhamento direcional com o resultado real, mas tambem um vies assimetrico: as previsoes do modelo tendiam a superestimar sistematicamente a fatia de votos democrata e subestimar a republicana. "Predicting Public Opinions Using Large Language Models" simula tanto a eleicao americana de 2024 quanto a eleicao federal alema de 2025, usando dados individuais para ajustar (recalibrar) as simulacoes do GPT contra resultados historicos de 2017 e 2021 antes de projetar 2025. "A Large-Scale Simulation on Large Language Models for Decision-Making in Political Science" roda simulacoes extensas para 2024 usando LLMs treinados apenas com dados anteriores a eleicao, com um pipeline de raciocinio em multiplos passos para prever o resultado em cada um dos 50 estados americanos. "Will Trump Win in 2024? Predicting the US Presidential Election via Multi-step Reasoning with Large Language Models" propoe explicitamente esse framework de raciocinio em etapas como melhoria sobre pedir a previsao diretamente ao modelo.

Fora do dominio eleitoral estrito, "Advancing Event Forecasting through Massive Training of Large Language Models" e "Do Large Language Models Know Conflict? Investigating Parametric vs. Non-Parametric Knowledge of LLMs for Conflict Forecasting" testam LLMs para previsao de eventos geopoliticos em geral (incluindo conflito armado), com a conclusao recorrente de que o conhecimento parametrico do modelo (o que ele "sabe" do treinamento) e insuficiente sozinho e precisa ser complementado por recuperacao de dados atualizados (RAG) ou por dados estruturados externos.

Leitura para o projeto: LLMs sao um desafiante experimental interessante e barato de testar (nao exige treinar nada, apenas prompting), mas o vies documentado exige que qualquer previsao gerada por LLM entre no backtest com o mesmo rigor que qualquer outro modelo — nunca deve ser usada sem calibracao contra o historico do proprio projeto.

## Modelagem baseada em agentes (agent-based modeling, ABM)

ABM simula eleitores individuais como agentes com regras de decisao (influenciadas por caracteristicas socioeconomicas, rede social, exposicao a informacao) e agrega o resultado da simulacao para gerar uma previsao — uma abordagem inteiramente independente de pesquisas de opiniao. "Forecasting elections with agent-based modeling: Two live experiments" (PLOS ONE, 2022) descreve uma plataforma que combina resultados historicos e modelos de simulacao para capturar como eleitores votaram no passado e projetar como votarao na proxima eleicao, testada ao vivo em dois pleitos reais. "Agent-based Simulation of District-based Elections" (arXiv) aplica a tecnica a eleicoes distritais, explorando dinamica de eleitor indeciso durante a campanha.

A vantagem central de ABM e permitir previsao com meses ou ate um ano de antecedencia, sem depender de pesquisa, alem de gerar interpretabilidade por bloco de eleitor (por exemplo, "eleitores de renda media em areas urbanas"). A desvantagem e a dependencia forte da qualidade das regras comportamentais calibradas — um ABM mal calibrado pode parecer sofisticado e ainda assim errar sistematicamente. Nao ha, no momento, ABM validado para eleicoes brasileiras na literatura revisada; seria um projeto de pesquisa em si, nao um ajuste incremental.

## Combinacao de previsoes (teoria de ensemble)

A literatura de forecasting frequentemente encontra ganhos ao combinar previsoes, mas a teoria por tras disso e mais sutil do que "juntar tudo que existir". Bates e Granger (1969), no artigo fundador "The Combination of Forecasts", mostram que uma combinacao de duas previsoes pode ter erro quadratico medio menor que qualquer uma das duas isoladas, usando pesos baseados na matriz de erro estimada — uma logica identica a diversificacao de carteira em financas.

Na pratica, porem, existe o chamado **"forecast combination puzzle"**: em muitos estudos empiricos, a media simples entre modelos supera esquemas de peso mais sofisticados, porque a matriz de covariancia dos erros e dificil de estimar com poucas observacoes e o erro de estimacao dos pesos anula o ganho teorico de pesos otimos. Isso e documentado formalmente em "The forecast combination puzzle: A simple theoretical explanation" (ScienceDirect) e revisado em "Forecast combinations: an over 50-year review" (Wang e Hyndman, arXiv 2205.04216).

Nas competicoes de forecasting mais rigorosas do mundo (M4 e M5, organizadas por Spyros Makridakis), ensembles dominaram consistentemente os modelos individuais. No M4, o metodo FFORMA (vice-campeao) usa gradient boosting (XGBoost) como meta-modelo para aprender os pesos de combinacao a partir de meta-caracteristicas extraidas de cada serie temporal — uma forma de stacking supervisionado. No M5 (previsao de vendas do Walmart), as melhores solucoes tambem usaram ensemble com gradient boosting. O mesmo padrao aparece fora de forecasting economico: nas competicoes de previsao de gripe do CDC (FluSight, desde 2013), ensembles de multiplos modelos (estatisticos, mecanicistas e de ML) superaram consistentemente qualquer modelo individual em quase todas as temporadas, inclusive combinando ate 21 modelos via stacking.

O PollyVote e outro exemplo classico em eleicoes americanas: combina pesquisas, modelos quantitativos, mercados, especialistas e expectativas de eleitores, partindo da premissa de que erros diferentes tendem a se compensar.

Conclusao pratica para o projeto: a escolha atual de um `ensemble_disciplinado` que so aceita modelos aprovados no backtest, com peso proximo de uma media (nao um peso livremente otimizado por minimos quadrados), esta alinhada com a evidencia empirica — nao com uma limitacao, mas com o "puzzle" documentado na literatura.

Regra proposta (mantida e reforcada):

- baseline sempre entra;
- modelo so entra se MAE fora da amostra <= baseline em pelo menos dois criterios;
- peso proximo do inverso do erro, mas com teto para evitar que um unico modelo domine e sem tentar estimar covariancia de erro com poucas eleicoes disponiveis;
- limitar peso maximo de qualquer modelo nao baseline;
- reavaliar pesos a cada nova eleicao historica incorporada.

## Previsao de eventos correlatos: conflitos e epidemias

O pedido original desta revisao inclui "eventos similares" a eleicoes — no sentido de eventos politicos/sociais discretos, dificeis de prever, com dados esparsos e onde ensembles e modelos hibridos tambem dominam. Dois dominios sao especialmente informativos por analogia direta.

**Conflito armado e golpes de Estado.** O ViEWS (Violence and Impacts Early-Warning System), projeto do Peace Research Institute Oslo (PRIO) e da Uppsala University, produz previsoes mensais de conflito violento com ate tres anos de antecedencia e granularidade subnacional, usando um ensemble de classificadores de machine learning treinados sobre dados de conflito e governanca (Hegre et al., 2019, "ViEWS: A political violence early-warning system", Journal of Peace Research). Revisoes como "The promise of machine learning in violent conflict forecasting" (Data & Policy, Cambridge) discutem como ML passou a incorporar dados nao estruturados (noticias, midia social) alem dos bancos estruturados classicos (UCDP, ACLED), com o mesmo tipo de cuidado metodologico deste projeto: dados coletados por humanos mudam de criterio ao longo do tempo, o que contamina series historicas longas se nao for auditado.

**Epidemias e pandemias.** O desafio FluSight do CDC, ativo desde a temporada de gripe 2013/14, e um dos programas de forecasting mais bem documentados do mundo, com dez anos de previsoes submetidas por dezenas de equipes usando modelos estatisticos, mecanicistas, de ML e hibridos. A conclusao mais robusta, repetida em varios artigos ("Accuracy of real-time multi-model ensemble forecasts for seasonal influenza in the U.S.", PLOS Computational Biology; "A Decade of CDC FluSight Influenza Forecasting", medRxiv 2026), e que o **ensemble do FluSight superou modelos individuais em praticamente todas as temporadas**, inclusive em temporadas atipicas (alta severidade, timing incomum) — o paralelo mais direto com a estrategia de ensemble disciplinado ja adotada neste projeto.

Leitura conjunta para o projeto: em tres dominios completamente diferentes (eleicoes, conflito armado, epidemias), a literatura converge para a mesma receita — bons modelos individuais, avaliados por backtest rigoroso e fora da amostra, combinados de forma conservadora, com o ensemble quase sempre vencendo qualquer modelo isolado a longo prazo.

## Sistemas multipartidarios e caso brasileiro

O Brasil exige mais cuidado que modelos bipartidarios dos EUA. Ha primeiro turno multipartidario, segundo turno, candidatos substitutos, variacao forte de coligacoes, voto util, rejeicao e diferentes cenarios de pesquisa. Modelos para EUA frequentemente trabalham com voto bipartidario; aqui precisamos modelar participacao relativa entre varios candidatos. A literatura de sistemas multipartidarios (Stoetzer et al. 2019; Dirichlet regression para eleicoes multipartidarias; o projeto Zweitstimme na Alemanha) e o ponto de partida metodologico mais proximo do problema brasileiro, mais proximo do que a maior parte da literatura americana citada nas secoes anteriores.

Implicacoes praticas:

- converter pesquisas para votos validos e importante, mas nao se deve forcar candidatos listados a somar 100 quando a tabela e parcial;
- cenarios diferentes nao devem ser misturados sem rotulo;
- brancos, nulos e indecisos precisam entrar como informacao;
- rejeicao e potencial de voto podem ser mais importantes no Brasil que em sistemas bipartidarios;
- previsao de primeiro turno e previsao de segundo turno devem ser modelos separados;
- regressao de Dirichlet e modelos Bayesianos multipartidarios (Stoetzer et al.) sao candidatos mais adequados que adaptar diretamente um modelo bipartidario americano.

## Metodos usados no projeto e justificativa

| Modelo usado | Justificativa na literatura | Papel atual |
|---|---|---|
| `baseline_pesquisa` | Agregacao de pesquisas e o padrao empirico perto da eleicao | Previsao principal |
| `baseline_ajustado` | Correcao por vies historico e qualidade do instituto | Camada auxiliar |
| `baseline_efeito_casa` | Correcao por vies historico de instituto-candidato | Melhor baseline atual |
| `bayesiano_dinamico_kalman` | Estado latente temporal estimado por Kalman, na linha de Linzer/Zweitstimme | Nowcast robusto em teste |
| `inferencial_ols` | Regressao explicavel para impacto de tempo, amostra e incumbencia | Diagnostico |
| `ridge` / `elastic_net` | Regularizacao reduz overfitting em muitos preditores | Desafiante ML |
| `huber` | Robustez contra outliers e tabelas ruidosas | Desafiante ML |
| `svr_rbf` | Nao linearidade controlada em base tabular | Melhor ML geral ate agora |
| `random_forest` / `random_forest_sqrt_600` / `random_forest_07_600` / `extra_trees` | Captura interacoes sem especificar formula; variantes testam `ntree` e `mtry`, na linha da literatura recente de ML para eleicoes | Comparativo, instavel |
| `gradient_boosting` / `ada_boost` | Aprende ajustes sequenciais de erro; boosting lidera em varios estudos recentes de ML eleitoral | Comparativo |
| `mlp_*` | Teste de rede neural tabular | Experimental |
| `voting_ia` / `stacking_ia` | Literatura de combinacao de previsoes (Bates-Granger, FFORMA) | Experimental ate vencer baseline |
| `ensemble_disciplinado` | Combina modelos aprovados por backtest geral ou vivo, evitando o "forecast combination puzzle" | Previsao final auxiliar |
| MRP (nao implementado) | Padrao para desagregacao subnacional (Gelman/Wang/Zweitstimme) | Candidato futuro |
| LLM como previsor (nao implementado) | Literatura de 2024-2026 mostra sinal com vies documentado | Candidato experimental |
| ABM (nao implementado) | Alternativa independente de pesquisa, horizonte longo | Candidato de pesquisa |

## Resultados aplicados: comparacao numerica com a literatura

Esta secao junta os numeros publicados de erro/acerto de cada metodo com os numeros que o proprio projeto ja produziu, para calibrar onde estamos. Aviso metodologico importante antes das tabelas: os numeros nao sao diretamente comparaveis em sentido estrito, porque diferem em pais, sistema partidario, horizonte de tempo antes da eleicao, e desenho do teste (leave-one-year-out entre eleicoes muito diferentes, no nosso caso, versus "ultima semana antes da eleicao" na maioria dos benchmarks americanos). Ainda assim, a ordem de grandeza e informativa.

### Tabela 1: erro em pontos percentuais de voto (MAE), mesma escala do nosso backtest

| Metodo / estudo | Contexto | MAE (pontos percentuais) | Leitura vs. este projeto |
|---|---|---|---|
| `baseline_pesquisa` (este projeto) | Brasil, 1994-2026, backtest geral leave-one-year-out | 6,03 | Referencia |
| `baseline_efeito_casa` (este projeto) | Idem | 6,43 (geral) / 7,47 (previsao viva) | Pior no geral, melhor na previsao viva |
| `bayesiano_dinamico_kalman` (este projeto) | Idem, previsao viva | 7,04 | Perto do baseline temporal |
| `gradient_boosting` (este projeto) | Idem, backtest geral | 6,69 | Proximo do baseline puro |
| ElecBERT-English (sentimento em texto, BERT) | EUA, eleicao 2020 | 6,13 | Praticamente igual ao nosso baseline_pesquisa |
| MRP (Isakov e Kuriwaki) | EUA 2016, RMSE de margem por estado | 6,7 (5,7 excluindo AK/HI/DC) | Mesma ordem de grandeza do nosso baseline |
| Pesquisas estaduais americanas, ultima quinzena | EUA 2020 (erro sistematico documentado pela AAPOR, "pior em 20 anos") | 4,3 (vies medio, nao MAE puro) | Erro menor, mas em eleicao bipartidaria com muito mais pesquisa por estado |
| Modelo hibrido fundamentos + pesquisa latente | Eleicoes estaduais alemas, 1990-2024, 2 meses antes | 3,09 | Metade do nosso erro; mesma familia do `bayesiano_dinamico_kalman` |
| Mesmo modelo hibrido | 2 semanas antes da eleicao | 2,19 | Erro cai com a proximidade, como esperado |
| Mesmo modelo hibrido | 2 dias antes da eleicao | 1,46 | Ordem de grandeza dos melhores agregadores do mundo |
| Iowa Electronic Markets (mercado de previsao) | EUA, 5 eleicoes 1988-2004, semana final | 1,5 (medio); vespera 1,33 | Consistente com o "hibrido alemao" 2 dias antes |
| RealClearPolitics, media de pesquisas | EUA, ultimos dias antes da eleicao (varias eleicoes) | ~1,5 | Mesma faixa do mercado de previsao |
| "Twitter puro" (estilo Tumasjan) | Alemanha 2009 | 1,65 (resultado contestado, nao replicado em outras eleicoes) | Nao deve ser tomado como referencia confiavel (ver secao de redes sociais) |
| Agent-based modeling (ABM), Taiwan 2020 | Previsao ao vivo, grupo A / grupo B | 0,21 / 0,87 | Caso pontual muito favoravel; nao ha equivalente testado no Brasil |

Leitura central: o nosso baseline de ~6 pontos de erro nao e ruim para o desenho de teste mais dificil que existe (leave-one-year-out cobrindo 1994 a 2026, com mudanca de sistema partidario, poucos institutos rastreados nos anos antigos e cenarios de candidatos completamente diferentes a cada eleicao). Ele fica na mesma familia do MRP americano (que tambem e medido no nivel "por unidade geografica/tempo", nao "ultima semana") e do ElecBERT (que usa uma fonte de dado totalmente diferente, texto, e ainda assim converge para o mesmo patamar de erro). Os numeros de 1 a 2 pontos percentuais (mercados de previsao, agregadores finais americanos, hibrido alemao a poucos dias da eleicao) sao o "teto de excelencia" da literatura, mas medidos em contextos muito mais favoraveis: eleicoes bipartidarias ou quase-bipartidarias, com dezenas de pesquisas por semana e horizonte de 2 dias, nao de anos. Nao e uma comparacao justa esperar que o baseline atual do projeto chegue nesse patamar sem uma base de pesquisas brasileira tao densa quanto a americana perto da eleicao.

### Tabela 2: classificacao do vencedor (accuracy, nao MAE)

Estes numeros medem uma tarefa diferente (acertar quem vence, nao o quanto cada um tira de voto) e nao devem ser misturados com a Tabela 1.

| Metodo / estudo | Contexto | Acerto do vencedor | Observacao |
|---|---|---|---|
| Random Forest (estudo de ML eleitoral generico) | Dataset de treino/teste do proprio estudo | 97% | Tarefa de classificacao binaria, dataset favoravel |
| Gradient Boosting Trees / MLP | Idem | 96% | Idem |
| RNN | Idem | 91,6% | Idem |
| LLM (GPT-4o), decodificacao "wisdom of crowds" | EUA 2024, estados-chave/swing states | 66,7% a 86,7% conforme metodo de decodificacao | Vies pro-democrata documentado; pior justamente nos estados decisivos |
| ABM (agent-based modeling) | EUA 2020, 6 estados | 6 de 6 corretos | Amostra pequena (6 estados), nao generalizavel |
| Institutos brasileiros (Datafolha/Ipec-Ibope) | Segundo turno, Brasil, desde 2006 | Vencedor sempre dentro da margem de erro | Primeiro turno e mais dificil: 2014 foi o pior ano, com os 3 primeiros colocados fora da margem de erro de 2 pontos nos dois institutos |

Leitura: os numeros de "97% de acerto" de ML citados em varios artigos populares usam desenhos de teste bem mais faceis (classificacao binaria com dataset de treino/teste do mesmo periodo, nao backtest cronologico entre eleicoes diferentes) do que o backtest que este projeto usa. Isso e um alerta de comparabilidade, nao uma evidencia de que ML "funciona melhor" do que os baselines deste projeto.

### Tabela 3: calibracao probabilistica (Brier score)

| Metodo / estudo | Contexto | Brier score | Observacao |
|---|---|---|---|
| Superforecasters (top 2%, Good Judgment Project) | Torneios geopoliticos IARPA, 2011-2015 | < 0,12 | Ficaram acima do percentil 90 mesmo contra equipes de especialistas |
| Algoritmo de agregacao do GJP | Idem | Superou 99,8% dos previsores individuais | Combinacao > individuo, mesmo com humanos |
| Referencia teorica | Brier = 0,25 equivale a "sempre 50/50"; Brier = 0 e perfeito | — | Escala de leitura |
| Este projeto | Probabilidade simulada de liderar/ir ao segundo turno, calibrada por erro historico | Nao calculado formalmente ainda | Recomendacao: calcular Brier score do ensemble contra o historico de 1994-2026 como proximo passo de avaliacao |

### Tabela 4: ganho de combinar previsoes (ensembles)

| Estudo | Contexto | Ganho de erro reportado | Comparacao com este projeto |
|---|---|---|---|
| Graefe et al. (peritos + pesquisas + fundamentos) | EUA, eleicoes de 2004 a 2016 | -19% no erro das pesquisas; -24% no erro dos peritos | Ganho grande porque combina 3 fontes bem diferentes entre si |
| Conservative forecasting / "Golden Rule" (Armstrong, Green, Graefe) | 154 eleicoes, 10 paises | -14% (Australia, 2 modelos) a -36% (EUA, 8 modelos); ate -43% ao incorporar mais variaveis | Ganho cresce com o numero e a diversidade de modelos combinados |
| FFORMA / M4 competition | 100.000 series temporais, forecasting geral | ate -9,4% de sMAPE sobre o benchmark de combinacao simples | Ganho menor porque a base de comparacao ja e um ensemble |
| FluSight (CDC, gripe) | EUA, 10 temporadas | Ensemble no top-5 em quase todas as temporadas (2a lugar em 2021/22, 5a em 2022/23) | Ganho consistente, mas nao um numero unico fixo |
| Ensemble deste projeto (`baseline_efeito_casa` + `bayesiano_dinamico_kalman`) | Brasil, previsao viva | ~2,5% (7,47 para 7,66 do baseline_pesquisa isolado) | Ganho modesto, coerente com o "forecast combination puzzle": poucas eleicoes brasileiras independentes limitam o quanto combinar ajuda |

Leitura central desta tabela: os maiores ganhos de combinacao na literatura (14% a 43%) vem de misturar fontes de informacao muito diferentes entre si (peritos humanos, pesquisas, fundamentos, varios paises). O ganho pequeno do ensemble deste projeto nao e uma falha de implementacao; e o resultado esperado quando as fontes combinadas (pesquisa ponderada e modelo de estado latente) sao parcialmente redundantes e a amostra de eleicoes historicas e pequena — exatamente o cenario em que o "forecast combination puzzle" preve que a media simples e dificil de superar.

## Recomendacao para a proxima versao

Prioridade 1: melhorar o baseline.

- efeito de casa por instituto;
- erro historico por instituto;
- suavizacao temporal;
- incerteza calibrada por backtest;
- separacao clara de cenarios principais e alternativos.

Prioridade 2: fundamentos objetivos.

- aprovacao do governo;
- desemprego;
- inflacao;
- crescimento do PIB;
- renda real;
- rejeicao;
- dummy de incumbencia e sucessor governista, ja iniciadas.

Prioridade 3: Bayesiano dinamico.

- estado latente diario por candidato;
- pesquisas como observacoes ruidosas;
- priors de fundamentos (na linha do Zweitstimme);
- simulacao probabilistica do primeiro turno;
- avaliar regressao de Dirichlet como alternativa/complemento para o cenario multipartidario completo.

Prioridade 4: ML e IA disciplinados.

- manter varios modelos;
- avaliar por rolling backtest;
- avaliar por previsao viva;
- promover para ensemble apenas se vencer o baseline, com peso proximo de uma media simples entre aprovados (nao otimizacao livre de pesos).

Prioridade 5 (exploratoria, nao urgente):

- MRP se/quando houver pesquisas com microdados de respondente suficientes para poststratificar por regiao;
- LLM como desafiante experimental de baixo custo, sempre calibrado contra o backtest do projeto e nunca usado cru;
- Google Trends e sinal de redes sociais como variavel explicativa auxiliar de baixo peso, nunca como previsor unico;
- ABM como linha de pesquisa separada, caso o projeto queira previsao de longo prazo independente de pesquisa.

## Livros de referencia

1. Nate Silver. *The Signal and the Noise: Why So Many Predictions Fail — but Some Don't*. Penguin Press, 2012. Panorama acessivel sobre previsao probabilistica em varios dominios, incluindo o capitulo sobre o modelo de eleicoes do proprio FiveThirtyEight.
2. Philip E. Tetlock e Dan Gardner. *Superforecasting: The Art and Science of Prediction*. Crown, 2015. Base do programa de pesquisa do Good Judgment Project sobre julgamento humano calibrado.
3. James E. Campbell e James C. Garand (eds.). *Before the Vote: Forecasting American National Elections*. Sage, 2000. Colaboracao classica reunindo os principais modelos fundamentalistas e suas criticas.
4. Robert S. Erikson e Christopher Wlezien. *The Timeline of Presidential Elections: How Campaigns Do (and Do Not) Matter*. University of Chicago Press, 2012. Mostra quando pesquisas comecam a ter poder preditivo real ao longo do ciclo eleitoral.
5. Rob J. Hyndman e George Athanasopoulos. *Forecasting: Principles and Practice* (3rd ed.). OTexts, 2021. https://otexts.com/fpp3/ — referencia padrao (gratuita) de metodos estatisticos de forecasting, incluindo combinacao de previsoes e avaliacao de erro, diretamente aplicavel ao pipeline deste projeto.
6. Trevor Hastie, Robert Tibshirani e Jerome Friedman. *The Elements of Statistical Learning* (2nd ed.). Springer, 2009. Referencia padrao de ML estatistico (regularizacao, arvores, boosting) usada por praticamente todos os modelos de ML tabular deste projeto.
7. Ian Goodfellow, Yoshua Bengio e Aaron Courville. *Deep Learning*. MIT Press, 2016. Referencia padrao de redes neurais, incluindo os fundamentos de MLP e redes recorrentes usados como ponto de partida antes de Transformers.

## Fontes principais (artigos e projetos)

### Agregacao de pesquisas e fundamentos

1. Alan Abramowitz. "Forecasting the 2008 Presidential Election with the Time-for-Change Model." PS: Political Science & Politics, 2008. https://www.jstor.org/stable/20452296
2. Douglas A. Hibbs Jr. "Bread and Peace Voting in U.S. Presidential Elections." Public Choice, 2000. https://ideas.repec.org/p/hhs/gunwpe/0020.html
3. Andrew Gelman e Gary King. "Why Are American Presidential Election Campaign Polls so Variable When Votes Are so Predictable?" British Journal of Political Science, 1993. https://gking.harvard.edu/publications/why-are-american-presidential-election-campaign-polls-so-variable-when-votes-are-so
4. Michael S. Lewis-Beck e Mary Stegmaier. "Election Forecasting, Scientific Approaches." Springer Encyclopedia of Social Network Analysis and Mining, 2016. https://link.springer.com/rwe/10.1007/978-1-4614-7163-9_63-1
5. FiveThirtyEight / ABC News. "How 538's 2024 presidential election forecast works." 2024. https://abcnews.go.com/538
6. The Economist. "President - Forecasting the US 2020 elections." 2020. https://projects.economist.com/us-2020-forecast/president

### MRP e previsao subnacional

7. Rob Wang, David Rothschild, Sharad Goel e Andrew Gelman. "Forecasting elections with non-representative polls." International Journal of Forecasting, 2015.
8. Yair Ghitza e Andrew Gelman. "Deep Interactions with MRP: Election Turnout and Voting Patterns Among Small Electoral Subgroups." https://sites.stat.columbia.edu/gelman/research/published/misterp.pdf
9. Rachel Isakov e Shiro Kuriwaki. "Predicting State Presidential Election Results Using National Tracking Polls and Multilevel Regression with Poststratification (MRP)." Public Opinion Quarterly, 82(3), 2020. https://academic.oup.com/poq/article-abstract/82/3/419/5052272
10. YouGov. "First YouGov MRP model of the 2025 German election shows gains for right." 2025. https://yougov.co.uk/international/articles/51394-first-yougov-mrp-model-of-the-2025-german-election-shows-gains-for-right
11. Focaldata. "How we successfully forecasted the German election results." https://www.focaldata.com/blog/how-we-successfully-forecasted-the-german-election-results

### Bayesiano dinamico e multipartidario

12. Drew A. Linzer. "Dynamic Bayesian Forecasting of Presidential Elections in the States." 2013. https://votamatic.org/
13. Merlin Heidemanns, Andrew Gelman e G. Elliott Morris. "An Updated Dynamic Bayesian Forecasting Model for the US Presidential Election." Harvard Data Science Review, 2020. https://hdsr.mitpress.mit.edu/pub/nw1dzd02/release/2
14. Linus F. Stoetzer et al. "Forecasting Elections in Multiparty Systems: A Bayesian Approach Combining Polls and Fundamentals." Political Analysis, 2019. https://ideas.repec.org/a/cup/polals/v27y2019i2p255-262_00.html
15. Hertie School. "Dynamic forecasting for Germany's federal 2025 election" (projeto Zweitstimme). https://www.hertie-school.org/en/news/detail/content/dynamic-forecasting-for-germanys-federal-2025-election
16. "The Zweitstimme Forecast for the German Federal Election 2025: Coalition Majorities and Vacant Districts." PS: Political Science & Politics, Cambridge Core.
17. "Forecasting multiparty by-elections using Dirichlet regression." International Journal of Forecasting, ScienceDirect.
18. "Picking the winner(s): Forecasting elections in multiparty systems." International Journal of Forecasting, ScienceDirect.

### Machine learning e deep learning

19. "Forecasting US Presidential Election 2024 using multiple machine learning algorithms." Munich Personal RePEc Archive, paper 122490. https://mpra.ub.uni-muenchen.de/122490/
20. "Predicting US Elections: A Machine Learning Approach." Research Square, 2024-2025. https://www.researchsquare.com/article/rs-5440358/v1
21. "Forecasting political voting: A high dimensional machine learning approach." ScienceDirect, 2025. https://www.sciencedirect.com/science/article/pii/S2666827025001227
22. "A Hybrid Method of Sentiment Analysis and Machine Learning Algorithm for the U.S. Presidential Election Forecasting." arXiv:2312.05584.
23. "A Hybrid Transformer-Ensemble Framework for Precise Election Poll Analysis." Computers, 2026. https://doi.org/10.3390/computers15080481
24. "Prediction of the 2023 Turkish Presidential Election Results Using Social Media Data." arXiv:2305.18397.
25. "A Survey of Deep Learning for Time Series Forecasting: Theories, Datasets, and State-of-the-Art Techniques." arXiv:2503.10198.
26. "A survey of transformer networks for time series forecasting." ScienceDirect, 2025.

### Texto, sentimento e redes sociais

27. Andranik Tumasjan, Timm O. Sprenger, Philipp G. Sandner e Isabell M. Welpe. "Predicting Elections with Twitter: What 140 Characters Reveal About Political Sentiment." ICWSM, 2010.
28. "On voting intentions inference from Twitter content: a case study on UK 2010 General Election." arXiv:1204.0423.
29. "Sentiment of tweets and socio-economic characteristics as the determinants of voting behavior at the regional level. Case study of 2019 Polish parliamentary election." arXiv:2010.03493.
30. "On the frontiers of Twitter data and sentiment analysis in election prediction: a review." ResearchGate, 2023.
31. "Stop trying to predict elections only with twitter – There are other data sources and technical issues to be improved." ScienceDirect.

### Big data, buscas e mercados de previsao

32. "Using Search Query Data to Predict the General Election: Can Google Trends Help." DiVA portal. https://www.diva-portal.org/smash/get/diva2:1439161/FULLTEXT01.pdf
33. "Can we predict multi-party elections with Google Trends data? Evidence across elections, data windows, and model classes." ResearchGate, 2024.
34. Justin Wolfers e Eric Zitzewitz. "Prediction Markets." NBER Working Paper, 2004. https://www.nber.org/system/files/working_papers/w12083/w12083.pdf
35. "Prediction Market Accuracy in the Long Run." https://www.biz.uiowa.edu/faculty/trietz/papers/long%20run%20accuracy.pdf
36. "Are Betting Markets Better than Polling in Predicting Political Elections?" arXiv:2507.08921.

### Superforecasting, LLMs e modelagem baseada em agentes

37. AI Impacts. "Evidence on good forecasting practices from the Good Judgment Project." https://aiimpacts.org/evidence-on-good-forecasting-practices-from-the-good-judgment-project/
38. "What do forecasting rationales reveal about thinking patterns of top geopolitical forecasters?" ScienceDirect, 2021.
39. "Using Large Language Models to Forecast the 2024 U.S. Presidential Election: Accuracy, Bias, and Media Influence." Behavioural and Social Computing, 2025.
40. "Predicting Public Opinions Using Large Language Models." arXiv:2411.01582.
41. "A Large-Scale Simulation on Large Language Models for Decision-Making in Political Science." arXiv:2412.15291.
42. "Will Trump Win in 2024? Predicting the US Presidential Election via Multi-step Reasoning with Large Language Models." arXiv:2411.03321.
43. "Advancing Event Forecasting through Massive Training of Large Language Models: Challenges, Solutions, and Broader Impacts." arXiv:2507.19477.
44. "Do Large Language Models Know Conflict? Investigating Parametric vs. Non-Parametric Knowledge of LLMs for Conflict Forecasting." arXiv:2505.09852.
45. "Forecasting elections with agent-based modeling: Two live experiments." PLOS ONE, 2022. https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0270194
46. "Agent-based Simulation of District-based Elections." arXiv:2205.14400.

### Combinacao de previsoes e eventos correlatos

47. J. M. Bates e C. W. J. Granger. "The Combination of Forecasts." Journal of the Operational Research Society, 1969. https://link.springer.com/article/10.1057/jors.1969.103
48. "The forecast combination puzzle: A simple theoretical explanation." International Journal of Forecasting, ScienceDirect.
49. Xiaoqian Wang e Rob J. Hyndman. "Forecast combinations: an over 50-year review." arXiv:2205.04216.
50. Andreas Graefe, J. Scott Armstrong, Randall J. Jones Jr. e Alfred G. Cuzan. "Combining Forecasts for U.S. Presidential Elections." https://uwf.edu/
51. PollyVote. "About the PollyVote." https://www.pollyvote.com/
52. Håvard Hegre et al. "ViEWS: A political violence early-warning system." Journal of Peace Research, 2019. https://journals.sagepub.com/doi/full/10.1177/0022343319823860
53. "The promise of machine learning in violent conflict forecasting." Data & Policy, Cambridge Core.
54. "Accuracy of real-time multi-model ensemble forecasts for seasonal influenza in the U.S." PLOS Computational Biology. https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1007486
55. "A Decade of CDC FluSight Influenza Forecasting." medRxiv, 2026.

### Brasil

56. Wagner G. Gramacho. "A margem das margens? A precisao das pesquisas pre-eleitorais." 2013. https://www.scielo.br/
57. Jairo Nicolau. "An Analysis of the 2002 Presidential Elections Using Logistic Regression." https://bibliotecadigital.tse.jus.br/
58. Pedro Santos Mundim. "Imprensa e voto nas eleicoes presidenciais brasileiras de 2002 e 2006." https://periodicos.sbu.unicamp.br/
59. TSE. "Pesquisas eleitorais / PesqEle." https://www.tse.jus.br/

### Resultados aplicados e comparacoes numericas

60. Andreas Graefe, Alfred Cuzan, J. Scott Armstrong e Randall J. Jones Jr. "Combining forecasts: An application to elections." International Journal of Forecasting, 2014.
61. J. Scott Armstrong e Andreas Graefe. "Predicting elections: Experts, polls, and fundamentals." Judgment and Decision Making, 2018. https://www.cambridge.org/core/journals/judgment-and-decision-making/article/predicting-elections-experts-polls-and-fundamentals/BB489BC5BF5BD68FBA229C1BBB277B39
62. Andreas Graefe, Kesten C. Green e J. Scott Armstrong. "Accuracy gains from conservative forecasting: Tests using variations of 19 econometric models to predict 154 elections in 10 countries." PLOS ONE, 2019. https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0209850
63. Langer Research Associates / AAPOR. "Predicting 2016 State Presidential Election Results with a Multilevel Regression and Poststratification Approach." https://www.langerresearch.com/wp-content/uploads/AAPOR-MRP_LangerResearch.pdf
64. AAPOR Task Force on 2020 Pre-Election Polling. Relatorio final, 2021. https://aapor.org/wp-content/uploads/2022/11/AAPOR-Task-Force-on-2020-Pre-Election-Polling_Report-FNL.pdf
65. "An election forecasting model for subnational elections" (modelo hibrido de fundamentos e pesquisa latente, eleicoes estaduais alemas 1990-2024). International Journal of Forecasting, ScienceDirect, 2025. https://www.sciencedirect.com/science/article/pii/S0261379425000459
66. "Improving Sentiment Analysis in Election-Based Conversations on Twitter with ElecBERT Language Model." Computers, Materials & Continua, ScienceDirect, 2023.
67. Spyros Makridakis et al. "The M4 Competition: 100,000 time series and 61 forecasting methods" e "The M4 competition: Conclusions." International Journal of Forecasting, 2020.
68. Mellers, Tetlock et al. "Identifying and Cultivating Superforecasters as a Method of Improving Probabilistic Predictions." Perspectives on Psychological Science, 2015. https://faculty.wharton.upenn.edu/wp-content/uploads/2015/07/2015---superforecasters.pdf
69. "The 2023/24 VIEWS Prediction Challenge: Predicting the Number of Fatalities in Armed Conflict, with Uncertainty." arXiv:2407.11045.
70. Congresso em Foco / CNN Brasil / O Povo. Reportagens de balanco sobre acerto e erro de pesquisas eleitorais brasileiras por eleicao (1989-2022), usadas como referencia jornalistica do erro historico de institutos no Brasil — nao substituem auditoria estatistica primaria.

## Nota metodologica desta revisao

Esta rodada foi feita com busca web direta (WebSearch) em ingles e portugues, sem acesso a um agregador academico dedicado (o servidor MCP de busca de artigos configurado nesta sessao falhou ao conectar). Os resumos de cada artigo acima vem dos abstracts/paginas indexadas retornadas pela busca, nao da leitura integral de cada PDF. Para uma revisao sistematica formal (com triagem de abstracts, matriz de qualidade metodologica e busca em bases como Scopus/Web of Science), recomenda-se repetir a busca com um plugin academico dedicado (ex. Consensus, SciSpace) ou acesso direto a essas bases, e verificar cada citacao no texto completo antes de basear uma decisao de modelagem exclusivamente nela.
