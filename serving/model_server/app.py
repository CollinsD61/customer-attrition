import os

from kserve import Model, ModelServer
from kserve.errors import ModelMissingError

from serving.model_server.feature_client import FeatureClient
from serving.model_server.model import ChurnModel
from serving.model_server.settings import settings


class ChurnKServeModel(Model):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._churn_model: ChurnModel | None = None
        self._feature_client: FeatureClient | None = None

    def load(self) -> None:
        feast_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "mlops", "feast"
        )
        self._feature_client = FeatureClient(
            repo_path=settings.FEAST_REGISTRY_PATH or feast_path
        )
        self._churn_model = ChurnModel(
            model_name=settings.MODEL_NAME,
        )

    def predict(self, payload: dict, headers: dict[str, str] | None = None) -> dict:
        if self._feature_client is None or self._churn_model is None:
            raise ModelMissingError("Model not loaded")

        instances = payload.get("instances", [payload])
        if not instances:
            instances = [payload]

        predictions = []
        for instance in instances:
            customer_id = instance.get("customer_id", "")
            features = self._feature_client.get_online_features(customer_id)
            feature_values = {k: v for k, v in features.items() if k != "customer_id"}
            result = self._churn_model.predict(feature_values)
            result["customer_id"] = customer_id
            predictions.append(result)

        return {"predictions": predictions}


if __name__ == "__main__":
    model = ChurnKServeModel(settings.MODEL_NAME)
    server = ModelServer()
    server.start([model])
