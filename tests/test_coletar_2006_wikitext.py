import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from coletar_2006_wikitext import parse_first_round


def test_parse_first_round_wikitext_block():
    text = '''
== Pesquisas ==
; Primeiro turno
<timeline>
  from:0 till:47 color:P width:20 align:left fontsize:S text:"Lula (49%)"
  from:0 till:33 color:P width:20 align:left fontsize:S text:"Geraldo Alckmin (35%)"
  from:0 till:8 color:P width:20 align:left fontsize:S text:"Helo�sa Helena (8%)"
  from:0 till:9 color:P width:20 align:left fontsize:S text:"Votos brancos e nulos e Indecisos   (9%)"
TextData =
  pos:(160,215) fontsize:M text:"Pesquisa 30/09/06"
  pos:(180,205) fontsize:S text:"Fonte: Datafolha"
</timeline>
* Total de entrevistados: 7.528
== Influencia ==
'''

    rows = parse_first_round(text)

    assert len(rows) == 3
    assert rows[0]["data_publicacao"] == "2006-09-30"
    assert rows[0]["amostra"] == "7528"
    assert rows[0]["candidato"] == "Lula"
    assert rows[0]["percentual_total"] == "49"
    assert rows[2]["candidato"] == "Heloísa Helena"
    assert rows[2]["indecisos"] == "9"
