import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from avaliar_rolling import chronological_splits


def test_chronological_splits_train_only_past_elections():
    df = pd.DataFrame({"ano_eleicao": [2010, 2014, 2018, 2022]})

    splits = list(chronological_splits(df, [2018, 2022]))

    assert splits[0][0] == 2018
    assert splits[0][1]["ano_eleicao"].tolist() == [2010, 2014]
    assert splits[1][0] == 2022
    assert splits[1][1]["ano_eleicao"].tolist() == [2010, 2014, 2018]
