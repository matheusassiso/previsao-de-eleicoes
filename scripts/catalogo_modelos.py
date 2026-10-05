from __future__ import annotations

import warnings

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    AdaBoostRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
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

warnings.filterwarnings(
    "ignore",
    message="`sklearn.utils.parallel.delayed` should be used.*",
    category=UserWarning,
)

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
    "dias_publicacao_ate_eleicao",
    "ordem_pesquisa_instituto_cenario",
    "ordem_pesquisa_campanha",
    "amostra_imputada",
    "cenario_prioridade",
]
FEATURES_CAT = ["instituto", "cenario_rotulo", "qualidade_fonte"]
FEATURES = FEATURES_NUM + FEATURES_CAT
EVAL_MODELS_INTENSIVE = [
    "ridge",
    "huber",
    "elastic_net",
    "ridge_forte",
    "random_forest_07_600",
    "random_forest_05_1200",
    "random_forest_sqrt_1200",
    "random_forest_03_1600_leaf1",
    "random_forest_05_1600_leaf1",
    "random_forest_07_1600_leaf1",
    "random_forest_sqrt_1600_leaf1",
    "random_forest_log2_1600_leaf1",
    "random_forest_05_2000_leaf3",
    "extra_trees",
    "extra_trees_1000",
    "extra_trees_03_1600_leaf1",
    "extra_trees_05_1600_leaf1",
    "extra_trees_sqrt_1600_leaf1",
    "extra_trees_log2_1600_leaf1",
    "extra_trees_05_2000_leaf3",
    "gradient_boosting",
    "gradient_boosting_slow",
    "gradient_boosting_deep",
    "hist_gradient_boosting",
    "hist_gradient_boosting_l2",
    "ada_boost",
    "mlp_pequena",
    "mlp_media",
    "mlp_profunda",
    "mlp_larga",
    "voting_ia",
    "stacking_ia",
    "voting_arvores_ia",
    "stacking_arvores_ia",
]


def make_tabular_model(estimator):
    preprocess = ColumnTransformer(
        [
            ("num", make_pipeline(SimpleImputer(strategy="constant", fill_value=0), StandardScaler()), FEATURES_NUM),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), FEATURES_CAT),
        ]
    )
    return make_pipeline(preprocess, estimator)


def model_catalog():
    ml = {
        "ridge": Ridge(alpha=1.0),
        "ridge_fraco": Ridge(alpha=0.2),
        "ridge_forte": Ridge(alpha=5.0),
        "elastic_net": ElasticNet(alpha=0.03, l1_ratio=0.2, max_iter=5000, random_state=42),
        "elastic_net_l1_05": ElasticNet(alpha=0.02, l1_ratio=0.5, max_iter=7000, random_state=142),
        "elastic_net_l1_08": ElasticNet(alpha=0.01, l1_ratio=0.8, max_iter=7000, random_state=143),
        "huber": HuberRegressor(max_iter=500),
        "huber_fino": HuberRegressor(epsilon=1.2, max_iter=800),
        "svr_rbf": SVR(C=10, epsilon=0.5),
        "svr_rbf_fino": SVR(C=30, epsilon=0.25),
        "random_forest": RandomForestRegressor(n_estimators=250, random_state=42),
        "random_forest_sqrt_600": RandomForestRegressor(n_estimators=600, max_features="sqrt", random_state=42, n_jobs=-1),
        "random_forest_07_600": RandomForestRegressor(n_estimators=600, max_features=0.7, random_state=43, n_jobs=-1),
        "random_forest_05_1200": RandomForestRegressor(n_estimators=1200, max_features=0.5, min_samples_leaf=2, random_state=44, n_jobs=-1),
        "random_forest_sqrt_1200": RandomForestRegressor(n_estimators=1200, max_features="sqrt", min_samples_leaf=2, random_state=45, n_jobs=-1),
        "random_forest_03_1600_leaf1": RandomForestRegressor(n_estimators=1600, max_features=0.3, min_samples_leaf=1, random_state=46, n_jobs=-1),
        "random_forest_05_1600_leaf1": RandomForestRegressor(n_estimators=1600, max_features=0.5, min_samples_leaf=1, random_state=47, n_jobs=-1),
        "random_forest_07_1600_leaf1": RandomForestRegressor(n_estimators=1600, max_features=0.7, min_samples_leaf=1, random_state=48, n_jobs=-1),
        "random_forest_sqrt_1600_leaf1": RandomForestRegressor(n_estimators=1600, max_features="sqrt", min_samples_leaf=1, random_state=49, n_jobs=-1),
        "random_forest_log2_1600_leaf1": RandomForestRegressor(n_estimators=1600, max_features="log2", min_samples_leaf=1, random_state=50, n_jobs=-1),
        "random_forest_05_2000_leaf3": RandomForestRegressor(n_estimators=2000, max_features=0.5, min_samples_leaf=3, random_state=51, n_jobs=-1),
        "extra_trees": ExtraTreesRegressor(n_estimators=250, random_state=42),
        "extra_trees_1000": ExtraTreesRegressor(n_estimators=1000, max_features=0.7, min_samples_leaf=2, random_state=46, n_jobs=-1),
        "extra_trees_03_1600_leaf1": ExtraTreesRegressor(n_estimators=1600, max_features=0.3, min_samples_leaf=1, random_state=52, n_jobs=-1),
        "extra_trees_05_1600_leaf1": ExtraTreesRegressor(n_estimators=1600, max_features=0.5, min_samples_leaf=1, random_state=53, n_jobs=-1),
        "extra_trees_sqrt_1600_leaf1": ExtraTreesRegressor(n_estimators=1600, max_features="sqrt", min_samples_leaf=1, random_state=54, n_jobs=-1),
        "extra_trees_log2_1600_leaf1": ExtraTreesRegressor(n_estimators=1600, max_features="log2", min_samples_leaf=1, random_state=55, n_jobs=-1),
        "extra_trees_05_2000_leaf3": ExtraTreesRegressor(n_estimators=2000, max_features=0.5, min_samples_leaf=3, random_state=56, n_jobs=-1),
        "gradient_boosting": GradientBoostingRegressor(random_state=42),
        "gradient_boosting_slow": GradientBoostingRegressor(n_estimators=400, learning_rate=0.03, max_depth=2, random_state=57),
        "gradient_boosting_deep": GradientBoostingRegressor(n_estimators=250, learning_rate=0.04, max_depth=3, min_samples_leaf=3, random_state=58),
        "hist_gradient_boosting": HistGradientBoostingRegressor(max_iter=500, learning_rate=0.04, l2_regularization=0.0, random_state=59),
        "hist_gradient_boosting_l2": HistGradientBoostingRegressor(max_iter=700, learning_rate=0.03, l2_regularization=0.2, random_state=60),
        "ada_boost": AdaBoostRegressor(random_state=42),
        "ada_boost_lento": AdaBoostRegressor(n_estimators=400, learning_rate=0.03, random_state=61),
    }
    deep = {
        "mlp_pequena": MLPRegressor(hidden_layer_sizes=(8,), max_iter=1200, random_state=42),
        "mlp_media": MLPRegressor(hidden_layer_sizes=(16, 8), max_iter=1500, random_state=43),
        "mlp_profunda": MLPRegressor(hidden_layer_sizes=(32, 16, 8), max_iter=1800, random_state=44),
        "mlp_larga": MLPRegressor(hidden_layer_sizes=(64, 32), alpha=0.001, max_iter=2200, random_state=62),
        "mlp_larga_regularizada": MLPRegressor(hidden_layer_sizes=(64, 32, 16), alpha=0.01, max_iter=2400, random_state=63),
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
        "voting_arvores_ia": VotingRegressor(
            [
                ("gb", GradientBoostingRegressor(n_estimators=250, learning_rate=0.04, max_depth=3, random_state=58)),
                ("rf", RandomForestRegressor(n_estimators=1200, max_features=0.5, min_samples_leaf=2, random_state=44, n_jobs=-1)),
                ("et", ExtraTreesRegressor(n_estimators=1000, max_features=0.7, min_samples_leaf=2, random_state=46, n_jobs=-1)),
            ]
        ),
        "stacking_arvores_ia": StackingRegressor(
            [
                ("gb", GradientBoostingRegressor(n_estimators=250, learning_rate=0.04, max_depth=3, random_state=58)),
                ("rf", RandomForestRegressor(n_estimators=1200, max_features=0.5, min_samples_leaf=2, random_state=44, n_jobs=-1)),
                ("et", ExtraTreesRegressor(n_estimators=1000, max_features=0.7, min_samples_leaf=2, random_state=46, n_jobs=-1)),
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
