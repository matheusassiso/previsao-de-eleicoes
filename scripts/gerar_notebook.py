from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "modelo_eleitoral_2026.ipynb"


def md(text: str):
    return nbf.v4.new_markdown_cell(text)


def code(text: str):
    return nbf.v4.new_code_cell(text)


nb = nbf.v4.new_notebook()
nb["cells"] = [
    md(
        "# Modelo eleitoral presidencial 2026\n\n"
        "Notebook espelhado do relatorio Quarto. Use para explorar dados, testar variaveis e comparar modelos."
    ),
    code(
        "from pathlib import Path\n"
        "import matplotlib.pyplot as plt\n"
        "import pandas as pd\n\n"
        "ROOT = Path('..')\n"
        "RAW = ROOT / 'data' / 'raw'\n"
        "PROCESSED = ROOT / 'data' / 'processed'\n\n"
        "def read_csv(path):\n"
        "    return pd.read_csv(path) if path.exists() else pd.DataFrame()\n\n"
        "polls = read_csv(PROCESSED / 'pesquisas_validos.csv')\n"
        "raw_polls = read_csv(RAW / 'pesquisas.csv')\n"
        "elections = read_csv(RAW / 'eleicoes.csv')\n"
        "forecasts = read_csv(PROCESSED / 'previsoes.csv')\n"
    ),
    md("## Base carregada"),
    code(
        "print('Pesquisas processadas:', len(polls))\n"
        "print('Pesquisas brutas:', len(raw_polls))\n"
        "print('Eleicoes cadastradas:', len(elections))\n"
        "print('Previsoes salvas:', len(forecasts))"
    ),
    md(
        "## Variaveis candidatas\n\n"
        "- Pesquisas: voto valido estimado, instituto, metodo, amostra, recencia.\n"
        "- Tempo: dias do fim do campo ate a eleicao, dias da publicacao ate a eleicao.\n"
        "- Ordem: sequencia da pesquisa no instituto/cenario e na campanha.\n"
        "- Fundamentos: incumbencia, sucessor governista, aprovacao, economia, rejeicao."
    ),
    code(
        "if polls.empty:\n"
        "    print('Ainda nao ha pesquisas processadas. Preencha data/raw/pesquisas.csv e rode scripts/preparar_dados.py.')\n"
        "else:\n"
        "    display(polls.head())"
    ),
    md("## Cobertura por instituto"),
    code(
        "data = polls if not polls.empty else raw_polls\n"
        "if data.empty or 'instituto' not in data:\n"
        "    print('Base de pesquisas ainda vazia.')\n"
        "else:\n"
        "    counts = data.drop_duplicates(['ano_eleicao', 'instituto', 'data_publicacao', 'cenario']).groupby('instituto').size().sort_values()\n"
        "    ax = counts.plot(kind='barh', figsize=(9, 5), title='Cobertura por instituto')\n"
        "    ax.set_xlabel('Pesquisas')\n"
        "    ax.set_ylabel('Instituto')\n"
        "    plt.show()"
    ),
    md("## Evolucao por candidato"),
    code(
        "if polls.empty or 'voto_valido_estimado' not in polls:\n"
        "    print('Sem serie temporal ainda.')\n"
        "else:\n"
        "    tmp = polls.copy()\n"
        "    tmp['data_publicacao'] = pd.to_datetime(tmp['data_publicacao'])\n"
        "    tmp['voto_valido_estimado'] = pd.to_numeric(tmp['voto_valido_estimado'])\n"
        "    latest_year = tmp['ano_eleicao'].max()\n"
        "    tmp = tmp[tmp['ano_eleicao'] == latest_year]\n"
        "    fig, ax = plt.subplots(figsize=(9, 5))\n"
        "    for candidate, group in tmp.groupby('candidato'):\n"
        "        series = group.groupby('data_publicacao')['voto_valido_estimado'].mean().sort_index()\n"
        "        ax.plot(series.index, series.values, marker='o', label=candidate)\n"
        "    ax.set_title(f'Evolucao das pesquisas em {latest_year}')\n"
        "    ax.set_ylabel('Votos validos estimados (%)')\n"
        "    ax.legend()\n"
        "    plt.show()"
    ),
]

nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "pygments_lexer": "ipython3"},
}

NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, NOTEBOOK)
print(f"Notebook gravado em {NOTEBOOK}")
