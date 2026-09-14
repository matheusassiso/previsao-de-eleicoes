from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    AdaBoostRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor,
    VotingRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet, HuberRegressor, Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVR

FEATURES_NUM = [
    "voto_valido_estimado",
    "dias_campo_ate_eleicao",
    "amostra",
    "incumbente",
    "sucessor_governo",
    "partido_governo",
    "reeleicao_permitida",
    "ex_presidente",
    "pib_crescimento",
    "inflacao",
    "desemprego",
    "fundamentos_defasagem_max",
]
FEATURES_CAT = ["instituto", "cenario_rotulo"]
FEATURES = FEATURES_NUM + FEATURES_CAT


def make_tabular_model(estimator):
    preprocess = ColumnTransformer(
        [
            ("num", make_pipeline(SimpleImputer(strategy="constant", fill_value=0), StandardScaler()), FEATURES_NUM),
            ("cat", OneHotEncoder(handle_unknown="ignore"), FEATURES_CAT),
        ]
    )
    return make_pipeline(preprocess, estimator)


def model_catalog():
    ml = {
        "ridge": Ridge(alpha=1.0),
        "elastic_net": ElasticNet(alpha=0.03, l1_ratio=0.2, max_iter=5000, random_state=42),
        "huber": HuberRegressor(max_iter=500),
        "svr_rbf": SVR(C=10, epsilon=0.5),
        "random_forest": RandomForestRegressor(n_estimators=250, random_state=42),
        "random_forest_sqrt_600": RandomForestRegressor(n_estimators=600, max_features="sqrt", random_state=42, n_jobs=-1),
        "random_forest_07_600": RandomForestRegressor(n_estimators=600, max_features=0.7, random_state=43, n_jobs=-1),
        "extra_trees": ExtraTreesRegressor(n_estimators=250, random_state=42),
        "gradient_boosting": GradientBoostingRegressor(random_state=42),
        "ada_boost": AdaBoostRegressor(random_state=42),
    }
    deep = {
        "mlp_pequena": MLPRegressor(hidden_layer_sizes=(8,), max_iter=1200, random_state=42),
        "mlp_media": MLPRegressor(hidden_layer_sizes=(16, 8), max_iter=1500, random_state=43),
        "mlp_profunda": MLPRegressor(hidden_layer_sizes=(32, 16, 8), max_iter=1800, random_state=44),
    }
    ai = {
        "voting_ia": VotingRegressor(
            [
                ("ridge", Ridge(alpha=1.0)),
                ("gb", GradientBoostingRegressor(random_state=42)),
                ("rf", RandomForestRegressor(n_estimators=150, random_state=42)),
            ]
        ),
        "stacking_ia": StackingRegressor(
            [
                ("ridge", Ridge(alpha=1.0)),
                ("gb", GradientBoostingRegressor(random_state=42)),
                ("rf", RandomForestRegressor(n_estimators=150, random_state=42)),
            ],
            final_estimator=Ridge(alpha=1.0),
        ),
    }

    catalog = {}
    for name, estimator in ml.items():
        catalog[name] = {"familia": "machine_learning", "model": make_tabular_model(estimator)}
    for name, estimator in deep.items():
        catalog[name] = {"familia": "deep_learning", "model": make_tabular_model(estimator)}
    for name, estimator in ai.items():
        catalog[name] = {"familia": "ia_ensemble", "model": make_tabular_model(estimator)}
    return catalog
