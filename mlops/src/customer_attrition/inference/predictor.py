import pandas as pd

from customer_attrition.inference.model_loader import ModelLoader

FEATURE_COLS = [
    "age",
    "annual_income",
    "dependents",
    "tenure",
    "monthlycharges",
    "totalcharges",
    "num_services",
    "customer_satisfaction",
    "num_complaints",
    "num_service_calls",
    "late_payments",
    "avg_monthly_gb",
    "days_since_last_interaction",
    "credit_score",
]


class Predictor:
    def __init__(
        self,
        model_name: str,
        stage: str = "Production",
        tracking_uri: str | None = None,
    ) -> None:
        self._model = ModelLoader(tracking_uri).load(model_name, stage)

    def predict_proba(self, features: pd.DataFrame) -> pd.Series:
        return self._model.predict_proba(features)[:, 1]

    def predict(self, features: pd.DataFrame) -> pd.Series:
        return self._model.predict(features)
