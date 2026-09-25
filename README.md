# Previsao de eleicoes

Projeto para acompanhar a eleicao presidencial de 2026 no Brasil com um modelo incremental baseado em pesquisas eleitorais historicas e atuais.

Status curto: veja `STATUS.md`.

## Painel online

- [Abrir o painel pelo GitHub Pages](https://matheusassiso.github.io/previsao-de-eleicoes/reports/relatorio-modelo-eleitoral.html?v=atualizar-tudo-20260925)
- [Abrir o HTML direto no repositório](reports/relatorio-modelo-eleitoral.html)

## Ideia

1. Guardar pesquisas em formato tabular.
2. Converter intencao total em votos validos.
3. Comparar pesquisas historicas com o resultado real do primeiro turno.
4. Aprender erro por tempo ate a eleicao, instituto e contexto.
5. Recalcular a previsao de 2026 sempre que uma nova pesquisa entrar.
6. Salvar cada previsao datada para ver como o modelo muda ao longo do tempo.

## Estrutura

- `data/raw/`: bases originais, sem limpeza.
- `data/processed/`: bases padronizadas para o modelo.
- `scripts/`: scripts de limpeza, modelagem e atualizacao.
- `notes/`: decisoes, fontes e observacoes metodologicas.

## Primeira versao do modelo

A primeira versao deve ser simples:

- converter cada pesquisa para votos validos;
- ponderar por recencia;
- ponderar por tamanho da amostra;
- estimar erro historico conforme dias ate a eleicao;
- aplicar correcao por instituto apenas quando houver historico suficiente;
- gerar intervalos de incerteza, nao apenas um vencedor.

## Proximo passo

Montar `data/raw/pesquisas.csv` com pesquisas historicas e atuais, usando uma linha por candidato em cada pesquisa/cenario.

## Rodar o baseline

```powershell
cd C:\Users\Matheus\Documents\Codex\previsao-de-eleicoes
python scripts\atualizar_tudo.py
```

Para gravar uma nova fotografia datada da previsao no historico:

```powershell
python scripts\atualizar_tudo.py --registrar-historico
```

## Coletar pesquisas historicas estruturadas

```powershell
python scripts\baixar_pesquisas_wikipedia.py
python scripts\normalizar_pesquisas_wikipedia.py
python scripts\limpar_pesquisas.py
```

## Renderizar o relatorio

```powershell
quarto render reports\relatorio-modelo-eleitoral.qmd
```

## Gerar notebook

```powershell
python scripts\gerar_notebook.py
```
