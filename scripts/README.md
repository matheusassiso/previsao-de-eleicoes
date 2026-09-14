# Scripts

Scripts planejados:

- `preparar_dados.py`: ler pesquisas e resultados, padronizar nomes e calcular votos validos.
- `coletar_fundamentos.py`: baixar fundamentos economicos anuais pre-eleicao no World Bank.
- `ajustes_literatura.py`: calcular qualidade historica, efeito casa e funcoes de ajuste do baseline.
- `limpar_pesquisas.py`: manter apenas cenarios historicos plausiveis de primeiro turno.
- `coletar_2002_uol.py`: extrair a tabela historica de 2002 do acervo Fernando Rodrigues/UOL.
- `data/raw/pesquisas_1994_1998_folha_manual.csv`: entradas manuais auditadas de pesquisas Datafolha publicadas pela Folha.
- `data/raw/pesquisas_1994_2006_folha_manual.csv`: complemento manual auditado para 1994 e 2006 publicado pela Folha.
- `data/raw/pesquisas_2026_agosto_setembro_manual.csv`: pesquisas recentes de agosto/setembro de 2026 com Renan Santos e candidatos menores.
- `coletar_2006_wikitext.py`: extrair pesquisas de primeiro turno de 2006 dos graficos em wikitexto.
- `prever.py`: gerar previsao atual usando o baseline.
- `rodar_modelos.py`: treinar ou registrar status dos modelos inferencial, machine learning, rede neural e ensemble.
- `avaliar_historico.py`: simular previsoes antigas para medir erro.
- `avaliar_janelas.py`: avaliar o erro do baseline em janelas antes da eleicao.
- `avaliar_previsao_viva.py`: simular previsoes feitas apenas com pesquisas ja publicadas em cada corte.
- `avaliar_rolling.py`: treinar em eleicoes passadas, prever 2018/2022 e gerar previsoes de 2026 por modelo.
- `gerar_ensemble.py`: criar pesos do ensemble com base no backtest.
- `bayesiano_dinamico.py`: gerar nowcast por estado latente dinamico via filtro de Kalman.
- `auditar_fontes.py`: resumir cobertura e problemas basicos por ano e fonte.

Rodar:

```powershell
python scripts\coletar_2006_wikitext.py
python scripts\coletar_2002_uol.py
python scripts\coletar_fundamentos.py
python scripts\preparar_dados.py
python scripts\ajustes_literatura.py
python scripts\rodar_modelos.py
python scripts\avaliar_historico.py
python scripts\avaliar_janelas.py
python scripts\avaliar_previsao_viva.py
python scripts\avaliar_rolling.py
python scripts\prever.py
python scripts\bayesiano_dinamico.py
python scripts\gerar_ensemble.py
python scripts\registrar_historico_previsoes.py
python scripts\auditar_fontes.py
```

Os scripts ja rodam com a base vazia e deixam os arquivos de saida prontos.
