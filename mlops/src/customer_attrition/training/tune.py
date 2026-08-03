from sklearn.model_selection import GridSearchCV

from customer_attrition.training.train import get_default_params


def tune_model(X_train, y_train, param_grid: dict | None = None, cv: int = 3) -> dict:
    from lightgbm import LGBMClassifier

    grid = param_grid or {
        "n_estimators": [100, 200],
        "learning_rate": [0.05, 0.1],
        "max_depth": [4, 6],
    }
    base = LGBMClassifier(**get_default_params())
    search = GridSearchCV(base, grid, cv=cv, scoring="roc_auc", n_jobs=-1)
    search.fit(X_train, y_train)
    return search.best_params_
