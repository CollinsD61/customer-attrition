import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "mlops" / "src"))

from customer_attrition.common.constants import CHURN
from customer_attrition.preprocessing.split import split_data
from customer_attrition.training.evaluate import evaluate_model, get_feature_importance
from customer_attrition.training.train import train_model

N_ROWS = 50


@pytest.fixture
def synthetic_df() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    df = pd.DataFrame(
        {
            "tenure": rng.integers(1, 72, N_ROWS),
            "age": rng.integers(18, 70, N_ROWS),
            "monthlycharges": rng.uniform(20, 120, N_ROWS).round(2),
            "annual_income": rng.uniform(30000, 120000, N_ROWS).round(2),
        }
    )
    df[CHURN] = ((df["tenure"] < 20) | (df["monthlycharges"] > 90)).astype(int)
    return df


@pytest.fixture
def split(synthetic_df):
    return split_data(
        synthetic_df, target_col=CHURN, test_size=0.2, val_size=0.2, random_state=42
    )


def test_train_model_returns_model_and_params(split):
    X_train, X_val, _, y_train, y_val, _ = split

    model, params = train_model(X_train, y_train, X_val, y_val)

    assert hasattr(model, "predict")
    assert isinstance(params, dict)
    assert params["random_state"] == 42


def test_evaluate_model_returns_metrics(split):
    X_train, X_val, X_test, y_train, y_val, y_test = split
    model, _ = train_model(X_train, y_train, X_val, y_val)

    metrics = evaluate_model(model, X_test, y_test)

    for key in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
        assert key in metrics
        assert isinstance(metrics[key], float)


def test_get_feature_importance_returns_sorted(split):
    X_train, X_val, _, y_train, y_val, _ = split
    model, _ = train_model(X_train, y_train, X_val, y_val)

    importance = get_feature_importance(model, list(X_train.columns))

    values = [row["importance"] for row in importance]
    assert values == sorted(values, reverse=True)
    assert len(importance) == X_train.shape[1]
