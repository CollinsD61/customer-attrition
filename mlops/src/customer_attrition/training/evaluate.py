from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_model(model, X_test, y_test) -> dict:
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
    }


def get_feature_importance(model, feature_names: list[str]) -> list[dict]:
    importances = list(zip(feature_names, model.feature_importances_))
    importances.sort(key=lambda x: x[1], reverse=True)
    return [{"feature": name, "importance": imp} for name, imp in importances]
