import sys
from types import ModuleType

import pandas as pd
from customer_attrition.inference.predictor import FEATURE_COLS, Predictor
from customer_attrition.inference.preprocessing import preprocess_for_inference
from customer_attrition.training.tune import tune_model


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": ["C1", "C2"],
            "signup_date": ["2022-01-01", "2023-01-01"],
            "age": [43, 31],
            "gender": ["Female", "Male"],
            "annual_income": [50000.0, 90000.0],
            "education": ["college", "master"],
            "marital_status": ["married", "single"],
            "dependents": [1, 0],
            "tenure": [2, 30],
            "contract": ["month-to-month", "two_year"],
            "payment_method": ["electronic_check", "credit_card"],
            "paperless_billing": ["Yes", "No"],
            "senior_citizen": [0, 0],
            "monthlycharges": [80.0, 60.0],
            "totalcharges": [160.0, 1800.0],
            "num_services": [2, 4],
            "has_phone_service": [1, 0],
            "has_internet_service": [1, 1],
            "has_online_security": [0, 1],
            "has_online_backup": [0, 1],
            "has_device_protection": [1, 1],
            "has_tech_support": [0, 1],
            "has_streaming_tv": [1, 1],
            "has_streaming_movies": [0, 0],
            "customer_satisfaction": [2.0, 8.0],
            "num_complaints": [3.0, 0.0],
            "num_service_calls": [5, 1],
            "late_payments": [2, 0],
            "avg_monthly_gb": [109.0, 63.0],
            "days_since_last_interaction": [16, 2],
            "credit_score": [None, 700.0],
            "churn": [1, 0],
        }
    )


def test_preprocess_for_inference_keeps_rows():
    df = preprocess_for_inference(_sample_df())
    assert len(df) == 2


def test_feature_cols_defined():
    assert isinstance(FEATURE_COLS, list)
    assert "tenure" in FEATURE_COLS


def test_predictor_requires_model(monkeypatch):
    fake_mlflow = ModuleType("mlflow")
    fake_lightgbm = ModuleType("mlflow.lightgbm")
    fake_lightgbm.load_model = lambda *args, **kwargs: object()
    fake_mlflow.lightgbm = fake_lightgbm
    monkeypatch.setitem(sys.modules, "mlflow", fake_mlflow)
    monkeypatch.setitem(sys.modules, "mlflow.lightgbm", fake_lightgbm)

    p = Predictor("churn-predictor", stage="Staging")
    assert p._model is not None


def test_tune_model_returns_params():
    from sklearn.datasets import make_classification

    X, y = make_classification(n_samples=50, n_features=5, random_state=42)
    params = tune_model(
        X, y, param_grid={"n_estimators": [10], "learning_rate": [0.1]}, cv=2
    )
    assert isinstance(params, dict)
    assert "n_estimators" in params
