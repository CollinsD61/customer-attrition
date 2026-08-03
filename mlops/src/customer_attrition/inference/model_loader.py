from typing import Any, Protocol

import numpy as np


class PredictableModel(Protocol):
    def predict(self, X: Any) -> np.ndarray: ...

    def predict_proba(self, X: Any) -> np.ndarray: ...


class ModelLoader:
    def __init__(self, tracking_uri: str | None = None) -> None:
        self._tracking_uri = tracking_uri

    def load(self, model_name: str, stage: str = "Production") -> PredictableModel:
        import mlflow

        if self._tracking_uri:
            mlflow.set_tracking_uri(self._tracking_uri)
        return mlflow.lightgbm.load_model(f"models:/{model_name}/{stage}")  # type: ignore[no-any-return]
