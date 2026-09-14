import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from catalogo_modelos import FEATURES, model_catalog


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
