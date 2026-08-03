from lightgbm import LGBMClassifier

DEFAULT_PARAMS: dict = {
    "n_estimators": 200,
    "learning_rate": 0.05,
    "max_depth": 6,
    "num_leaves": 31,
    "random_state": 42,
    "class_weight": "balanced",
    "verbose": -1,
}


def get_default_params() -> dict:
    return dict(DEFAULT_PARAMS)


def train_model(
    X_train, y_train, X_val, y_val, params: dict | None = None
) -> tuple[LGBMClassifier, dict]:
    default_params = get_default_params()
    model_params = {**default_params, **(params or {})}
    model = LGBMClassifier(**model_params)
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        eval_metric="auc",
    )
    return model, model_params
