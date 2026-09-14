# Referencial teorico

Preparado em 2026-09-14, a partir de `docs/revisao-literatura-metodos.md`.

## O que este documento e, e como difere da revisao de literatura

A revisao de literatura (`revisao-literatura-metodos.md`) e um mapeamento amplo: lista familias de metodos, estudos aplicados e resultados numericos, organizados por tecnica (pesquisas, fundamentos, MRP, ML, deep learning, redes sociais, mercados, LLMs, ABM, ensembles, eventos correlatos).

O referencial teorico tem outro objetivo: nao listar o que existe, e sim **selecionar e amarrar as teorias que justificam as escolhas de design deste projeto**. Cada pilar abaixo e uma teoria ou principio formal, com a logica interna de por que ele se aplica, e termina em uma frase explicita ligando a teoria a um modulo especifico do codigo (`scripts/*.py`). E o arcabouço conceitual que da suporte ao "porque construimos assim", nao apenas ao "o que outros construiram".

O documento esta organizado em sete pilares teoricos, uma sintese integradora e uma secao de delimitacao (o que foi deliberadamente deixado de fora e por que).

## Pilar 1: Teoria do voto retrospectivo e economia politica eleitoral

**Teoria.** V. O. Key Jr., em *The Responsible Electorate* (1966), propoe que o eleitor medio vota principalmente como juiz retrospectivo do desempenho do governo, nao como um planejador prospectivo de politicas futuras — "the electorate is not fundamentally in a mood of trust or distrust; it is fundamentally rational, judging retrospectively". Morris Fiorina, em *Retrospective Voting in American National Elections* (1981), formaliza essa intuicao num modelo onde o eleitor usa a experiencia vivida (economia, guerra, escandalos) como sinal de baixo custo cognitivo para decidir o voto, dispensando a necessidade de acompanhar plataformas detalhadas de politica publica. Essa e a base teorica dos modelos de "fundamentos" cobertos na revisao de literatura: Hibbs (Bread and Peace), Abramowitz (Time-for-Change) e Erikson e Wlezien (*The Timeline of Presidential Elections*) sao todos operacionalizacoes empiricas da teoria do voto retrospectivo, cada um escolhendo um subconjunto diferente de indicadores objetivos (crescimento economico, inflacao, baixas em guerra, aprovacao presidencial, tempo de partido no poder) como proxy do "julgamento" do eleitorado sobre o desempenho do governo.

**Por que se aplica ao projeto.** O Brasil tem um eleitorado que reage a inflacao, desemprego e crescimento do PIB de forma documentada na literatura nacional (Gramacho; Nicolau) mesmo com um sistema partidario muito mais fragmentado que o americano. A teoria retrospectiva nao exige bipartidarismo — exige apenas que exista um "campo governista" identificavel a ser julgado, o que e verdade mesmo em eleicoes brasileiras multipartidarias com um presidente ou sucessor claro.

**Operacionalizacao no projeto.** `scripts/coletar_fundamentos.py` traz PIB, inflacao e desemprego pre-eleicao do World Bank; `data/raw/variaveis_candidatos.csv` guarda incumbencia e sucessao governista. Essas variaveis entram no `inferencial_ols` e nos modelos supervisionados como a materializacao direta da teoria do voto retrospectivo.

## Pilar 2: Teoria da agregacao de informacao ("sabedoria das multidoes")

**Teoria.** O Teorema do Juri de Condorcet (Marquis de Condorcet, *Essai sur l'application de l'analyse a la probabilite des decisions rendues a la pluralite des voix*, 1785) mostra formalmente que, se cada "votante" individual tem probabilidade maior que 50% de estar certo e os erros sao independentes, a probabilidade de a maioria estar certa cresce em direcao a 1 conforme o numero de votantes aumenta. O mesmo principio estatistico — que agregar muitas estimativas ruidosas e independentes reduz o erro pela lei dos grandes numeros — e a base formal por tras da ideia popularizada por James Surowiecki em *The Wisdom of Crowds* (2004) e por tras de todo o desenho de agregacao de pesquisas eleitorais (FiveThirtyEight, The Economist, PollyVote). Cada pesquisa e uma estimativa ruidosa e nao perfeitamente independente (institutos compartilham metodologia, momento de coleta e erro sistematico regional); por isso os agregadores profissionais nao fazem media simples ingenua — ponderam por qualidade do instituto e corrigem por "efeito casa" (house effect), justamente para restaurar a condicao de erros o mais proximo possivel de independentes antes de agregar.

**Por que se aplica ao projeto.** A conversao de uma pesquisa individual em previsao (`baseline_pesquisa`) e um caso direto de agregacao de sinais ruidosos; a correcao por instituto (`baseline_ajustado`) e por instituto-candidato (`baseline_efeito_casa`) e a aplicacao pratica do cuidado teorico com a violacao da independencia entre pesquisas do mesmo instituto.

**Operacionalizacao no projeto.** `scripts/ajustes_literatura.py` (`institute_stats`, `house_effect_stats`, `poll_weight`, `weighted_average`) implementa exatamente essa correcao de vies sistematico antes da agregacao, e `data/processed/qualidade_institutos.csv` / `efeito_casa_instituto_candidato.csv` guardam os parametros estimados.

## Pilar 3: Modelos de espaco de estado e inferencia Bayesiana dinamica

**Teoria.** Rudolf Kalman, em "A New Approach to Linear Filtering and Prediction Problems" (*Journal of Basic Engineering*, 1960), formaliza o filtro que leva seu nome: um metodo recursivo para estimar o estado nao observado de um sistema dinamico a partir de uma sequencia de observacoes ruidosas, combinando de forma otima (no sentido de minimo erro quadratico) a previsao do modelo com a nova observacao, ponderando cada uma pela sua incerteza relativa. Aplicado a eleicoes, a intencao de voto "verdadeira" da populacao em cada instante e tratada como um estado latente que evolui suavemente no tempo (um passeio aleatorio ou processo autorregressivo), e cada pesquisa e uma observacao ruidosa desse estado — nao o estado em si. Linzer (2013), Heidemanns, Gelman e Morris (2020) e Stoetzer et al. (2019) sao aplicacoes desse arcabouco de espaco de estado a eleicoes presidenciais e multipartidarias.

**Por que se aplica ao projeto.** A intencao de voto de fato muda ao longo de uma campanha (efeito de debates, escandalos, coligacoes) e cada pesquisa observa esse valor com erro amostral e nao amostral. Tratar a serie de pesquisas como observacoes ruidosas de um estado latente, em vez de tratar cada pesquisa como a verdade, e exatamente o que a teoria do filtro de Kalman formaliza — e da um caminho estatisticamente principiado para separar "ruido de uma pesquisa isolada" de "mudanca real de opiniao".

**Operacionalizacao no projeto.** `scripts/bayesiano_dinamico.py`, usando `UnobservedComponents` do `statsmodels` (uma implementacao de modelo de espaco de estado linear-gaussiano estimado por filtro de Kalman), gera `bayesiano_dinamico_kalman` e a saida `data/processed/previsao_bayesiana_dinamica.csv`.

## Pilar 4: Teoria estatistica do aprendizado (vies-variancia, regularizacao, ensemble)

**Teoria.** Tres resultados formais sustentam o uso — e os limites — de ML/DL no projeto:

1. **Dilema vies-variancia** (Geman, Bienenstock e Doursat, "Neural Networks and the Bias/Variance Dilemma", *Neural Computation*, 1992): o erro esperado de qualquer estimador se decompoe em vies (erro sistematico por o modelo ser simples demais) e variancia (erro por o modelo se ajustar demais ao ruido de uma amostra especifica). Modelos flexiveis (redes neurais profundas, arvores nao podadas) tem baixo vies mas alta variancia; com poucas eleicoes historicas independentes, a variancia domina o erro total — exatamente o padrao observado no backtest do projeto, onde `mlp_pequena`, `ridge` e `huber` tiveram MAE muito pior (17-18) que o baseline simples.
2. **Bagging e florestas aleatorias** (Breiman, "Bagging Predictors", *Machine Learning*, 1996; "Random Forests", *Machine Learning*, 2001) e **boosting** (Freund e Schapire, "Experiments with a New Boosting Algorithm", 1996): duas estrategias formais para reduzir variancia (bagging, promediando arvores treinadas em reamostras) ou vies (boosting, corrigindo sequencialmente o erro residual). Sao a base teorica direta de `random_forest`, `extra_trees`, `gradient_boosting` e `ada_boost` no catalogo do projeto.
3. **Teorema "No Free Lunch"** (Wolpert e Macready, "No Free Lunch Theorems for Optimization", *IEEE Transactions on Evolutionary Computation*, 1997): nenhum algoritmo de aprendizado e universalmente superior a outro quando promediado sobre todos os problemas possiveis; a superioridade de um metodo depende da estrutura especifica dos dados. Esse resultado formal justifica manter um catalogo de varios modelos competindo por backtest em vez de assumir a priori que "ML e melhor" ou que "o baseline e melhor" — a resposta correta so pode vir de teste empirico no dominio especifico (eleicoes brasileiras), o que e exatamente o desenho do projeto.

**Por que se aplica ao projeto.** A pequena quantidade de eleicoes presidenciais brasileiras observadas (9 desde 1994) e uma amostra minuscula para qualquer padrao de ML moderno; a teoria do dilema vies-variancia explica formalmente por que isso favorece modelos simples e regularizados (Ridge, Elastic Net) ou de vies controlado (baseline de pesquisas) sobre modelos muito flexiveis.

**Operacionalizacao no projeto.** `scripts/catalogo_modelos.py` implementa o catalogo completo de ML tabular e deep learning tabular citado acima; `scripts/avaliar_historico.py`, `avaliar_janelas.py`, `avaliar_previsao_viva.py` e `avaliar_rolling.py` sao o mecanismo empirico de selecao entre modelos que o teorema No Free Lunch exige — nunca escolher um vencedor por teoria pura, sempre por backtest.

## Pilar 5: Teoria da combinacao de previsoes

**Teoria.** Bates e Granger, em "The Combination of Forecasts" (*Journal of the Operational Research Society*, 1969), provam formalmente — usando uma analogia direta com a teoria de diversificacao de carteira de Markowitz — que uma combinacao linear de duas previsoes pode ter erro quadratico medio estritamente menor que qualquer uma das duas isoladas, com o peso otimo determinado pela matriz de covariancia dos erros. A pratica empirica subsequente, porem, revelou o "forecast combination puzzle": a matriz de covariancia dos erros e dificil de estimar com poucas observacoes, e o erro de estimacao dos pesos frequentemente supera o ganho teorico de pesos otimos, fazendo a media simples (ou quase-simples) superar esquemas de peso sofisticados na pratica (documentado formalmente na literatura revisada em `revisao-literatura-metodos.md`, secao "Combinacao de previsoes"). Esse e o mesmo principio teorico por tras do dominio de ensembles nas competicoes M4/M5 de forecasting e no FluSight do CDC.

**Por que se aplica ao projeto.** Com apenas 9 eleicoes presidenciais historicas, estimar uma matriz de covariancia de erro confiavel entre os modelos do catalogo e estatisticamente inviavel — exatamente a condicao em que a teoria preve que pesos livremente otimizados vao piorar, nao melhorar, a previsao combinada.

**Operacionalizacao no projeto.** `scripts/gerar_ensemble.py` implementa deliberadamente uma regra conservadora (so aceitar modelos que vencem o baseline por pelo menos um criterio de backtest, com peso proximo do inverso do erro e teto de participacao), em vez de uma otimizacao livre de pesos — uma escolha de design diretamente justificada pelo "forecast combination puzzle", nao uma limitacao acidental.

## Pilar 6: Escolha social e sistemas multipartidarios

**Teoria.** Anthony Downs, em *An Economic Theory of Democracy* (1957), modela o eleitor e o candidato num espaco ideologico unidimensional, prevendo convergencia ao eleitor mediano em sistemas de dois partidos (o "teorema do eleitor mediano", de Duncan Black e formalizado por Downs). Maurice Duverger, em *Les partis politiques* (1951), propoe a "lei de Duverger": sistemas eleitorais de pluralidade em turno unico tendem ao bipartidarismo, enquanto sistemas proporcionais e de dois turnos (como o Brasil) favorecem a fragmentacao em multiplos partidos viaveis. Kenneth Arrow, em *Social Choice and Individual Values* (1951), prova que nenhuma regra de agregacao de preferencias individuais em uma escolha coletiva pode satisfazer simultaneamente um conjunto minimo de axiomas de racionalidade e justica quando ha tres ou mais opcoes — um resultado formal que explica por que sistemas com mais de dois candidatos viaveis (segundo turno, coligacoes, voto util) sao estruturalmente mais complexos de modelar do que uma escolha binaria.

**Por que se aplica ao projeto.** O Brasil, com sistema de dois turnos e representacao proporcional para o Legislativo, e exatamente o caso que a lei de Duverger preve como fragmentado, o que e visivel nos dados do projeto (ate 8+ candidatos com participacao relevante em alguns cenarios de 2026). Isso invalida a aplicacao direta de modelos desenhados para eleicoes bipartidarias americanas (onde o "eleitor mediano" de Downs e uma simplificacao razoavel) e justifica formalmente por que a revisao de literatura recomenda a familia de modelos multipartidarios (Stoetzer et al., Dirichlet regression, Zweitstimme) como a analogia estrutural mais proxima, nao os modelos americanos polls-only/polls-plus tradicionais.

**Operacionalizacao no projeto.** O tratamento de cenarios separados (`data/raw/cenarios.csv`), a nao-normalizacao forcada de candidatos parciais a somarem 100%, e a modelagem separada de primeiro e segundo turno documentada em `docs/schema-dados.md` sao respostas diretas de design a essa teoria — nao decisoes arbitrarias de engenharia de dados.

## Pilar 7: Julgamento probabilistico calibrado e regras de escore proprias

**Teoria.** Glenn Brier, em "Verification of Forecasts Expressed in Terms of Probability" (*Monthly Weather Review*, 1950), propoe o escore que leva seu nome: uma regra de pontuacao propria (*proper scoring rule*) que penaliza tanto previsoes erradas quanto previsoes mal calibradas (excesso ou falta de confianca), com a propriedade matematica de que a estrategia otima do previsor e sempre reportar sua crenca real, nunca uma probabilidade estrategicamente distorcida. O programa de pesquisa de Philip Tetlock (Good Judgment Project, IARPA, 2011-2015) usa exatamente essa metrica para treinar e selecionar "superforecasters", mostrando empiricamente que pontuar por Brier score e dar feedback iterativo melhora a calibracao probabilistica de forma mensuravel ao longo do tempo.

**Por que se aplica ao projeto.** Uma previsao eleitoral responsavel nao deve reportar apenas "quem vai vencer", mas com que probabilidade — e essa probabilidade deve ser calibrada (quando o modelo diz 70%, o candidato deve vencer aproximadamente 70% das vezes em situacoes comparaveis), nao apenas direcionalmente correta.

**Operacionalizacao no projeto.** `scripts/prever.py` gera `probabilidade_liderar` e `probabilidade_ir_ao_segundo_turno` por simulacao gaussiana calibrada pelo erro historico de cada modelo — a mesma logica de calibracao probabilistica por escore proprio. **Lacuna identificada:** o projeto ainda nao calcula o Brier score formal dessas probabilidades contra o historico de 1994-2026 (ja registrado como recomendacao na revisao de literatura, Tabela 3 de "Resultados aplicados"); isso fecharia o ciclo teoria-pratica deste pilar.

## Sintese integradora

| Pilar teorico | Autor(es) fundador(es) | Modulo do projeto | O que a teoria explica |
|---|---|---|---|
| Voto retrospectivo | Key (1966); Fiorina (1981); Hibbs; Abramowitz; Erikson e Wlezien | `coletar_fundamentos.py`, `inferencial_ols` | Por que fundamentos economicos entram como variavel explicativa |
| Agregacao de informacao | Condorcet (1785); Surowiecki (2004) | `ajustes_literatura.py` (`baseline_pesquisa`, `_ajustado`, `_efeito_casa`) | Por que agregar pesquisas reduz erro, e por que corrigir vies de instituto antes de agregar |
| Espaco de estado / Kalman | Kalman (1960); Linzer; Heidemanns-Gelman-Morris | `bayesiano_dinamico.py` | Por que tratar intencao de voto como estado latente, nao como valor observado direto |
| Vies-variancia e ensemble learning | Geman-Bienenstock-Doursat (1992); Breiman (1996, 2001); Freund-Schapire (1996); Wolpert-Macready (1997) | `catalogo_modelos.py`, `avaliar_*.py` | Por que modelos simples competem bem com poucas eleicoes, e por que a selecao deve ser empirica |
| Combinacao de previsoes | Bates e Granger (1969); "forecast combination puzzle" | `gerar_ensemble.py` | Por que o ensemble e conservador em vez de otimizar pesos livremente |
| Escolha social / multipartidarismo | Downs (1957); Duverger (1951); Arrow (1951) | `cenarios.csv`, modelagem separada de turnos | Por que o Brasil exige tratamento diferente de modelos bipartidarios americanos |
| Escore proprio e calibracao | Brier (1950); Tetlock (2015) | `prever.py` (`probabilidade_liderar`) | Por que reportar probabilidade calibrada, nao so o vencedor esperado |

Lida em conjunto, esta tabela mostra que cada modulo relevante do projeto ja corresponde a uma escolha teoricamente motivada, nao a uma decisao de engenharia arbitraria — o que da ao pipeline uma justificativa formal alem do resultado empirico de backtest.

## Delimitacao do referencial (o que foi deixado de fora, e por que)

Nem toda teoria coberta na revisao de literatura vira pilar aqui, porque um referencial teorico deve ser o minimo necessario para justificar o desenho atual, nao um catalogo completo:

- **Teoria de mercados eficientes** (base dos mercados de previsao, Wolfers e Zitzewitz) foi deixada de fora porque o projeto nao usa nem planeja usar dados de mercado de apostas — nao ha mercado de apostas eleitorais liquido e legal no Brasil comparavel ao IEM americano.
- **Teoria de redes e difusao de informacao** (base dos modelos de sentimento em redes sociais e do voter model com stubborn nodes) foi deixada de fora porque a literatura revisada documenta historico fraco de replicacao para esse tipo de sinal (ver "Texto, redes sociais e sentimento" na revisao), e o projeto nao coleta dado de rede social.
- **Teoria de agentes e simulacao social computacional** (base de ABM) foi deixada de fora porque exigiria calibrar regras comportamentais individuais para o eleitor brasileiro — um projeto de pesquisa em si, fora do escopo atual de agregacao de pesquisas e fundamentos.
- **Teoria da informacao e deep learning representacional** (base de Transformers/atencao) foi mencionada no Pilar 4 apenas por extensao da teoria de aprendizado estatistico geral; nao ganhou pilar proprio porque o projeto ainda nao implementa nenhuma arquitetura de atencao, apenas MLP simples.

Essas quatro exclusoes sao reversiveis: se o projeto decidir implementar mercados, redes sociais, ABM ou Transformers no futuro (ver "Prioridade 5" em `revisao-literatura-metodos.md`), o referencial teorico correspondente ja esta identificado e citado na revisao de literatura, bastando promove-lo a um pilar formal aqui quando a implementacao existir.
