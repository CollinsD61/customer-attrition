import mlflow
import mlflow.lightgbm
import numpy as np

from serving.model_server.settings import settings


class ChurnModel:
    def __init__(self, model_name: str, model_version: str | None = None) -> None:
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        model_uri = (
            f"models:/{model_name}/{model_version}"
            if model_version
            else f"models:/{model_name}/latest"
        )
        self._model = mlflow.lightgbm.load_model(model_uri)
        self._model_version = model_version or self._resolve_version(model_name)

    def _resolve_version(self, model_name: str) -> str:
        client = mlflow.tracking.MlflowClient()
        latest = client.get_latest_versions(model_name, stages=["Production"])
        if latest:
            return str(latest[0].version)
        latest = client.get_latest_versions(model_name, stages=["Staging"])
        return str(latest[0].version) if latest else "unknown"

    def predict(self, features: dict) -> dict:
        feature_vector = np.array([list(features.values())])
        proba = float(self._model.predict_proba(feature_vector)[0, 1])
        pred = int(proba >= 0.5)
        return {
            "churn_probability": proba,
            "prediction": pred,
            "model_version": self._model_version,
        }

    def predict_proba(self, features: dict) -> float:
        feature_vector = np.array([list(features.values())])
        return float(self._model.predict_proba(feature_vector)[0, 1])
