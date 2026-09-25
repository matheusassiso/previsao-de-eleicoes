import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from catalogo_modelos import EVAL_MODELS_INTENSIVE, FEATURES, model_catalog


def test_catalog_has_multiple_models_per_requested_family():
    catalog = model_catalog()
    families = {}
    for name, spec in catalog.items():
        families.setdefault(spec["familia"], []).append(name)

    assert len(families["machine_learning"]) >= 3
    assert len(families["deep_learning"]) >= 2
    assert len(families["ia_ensemble"]) >= 2
    assert "pib_crescimento" in FEATURES
    assert "inflacao" in FEATURES
    assert "desemprego" in FEATURES
    assert "dias_publicacao_ate_eleicao" in FEATURES
    assert "ordem_pesquisa_campanha" in FEATURES
    assert "qualidade_fonte" in FEATURES
    assert "random_forest_05_1200" in catalog
    assert "extra_trees_1000" in catalog
    assert "random_forest_05_1200" in EVAL_MODELS_INTENSIVE
    assert "extra_trees_1000" in EVAL_MODELS_INTENSIVE
