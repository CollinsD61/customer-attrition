from backend.app.core.exceptions import CustomerNotFoundError, PredictionError
from backend.app.services.feast_client import FeastClient
from backend.app.services.kserve_client import KServeClient


class PredictionService:
    def __init__(self, feast_client: FeastClient, kserve_client: KServeClient) -> None:
        self._feast = feast_client
        self._kserve = kserve_client

    def predict(self, customer_id: str) -> dict:
        try:
            features = self._feast.get_online_features(customer_id)
            feature_values = {k: v for k, v in features.items() if k != "customer_id"}
            if not feature_values:
                raise CustomerNotFoundError(
                    f"Customer {customer_id} not found in feature store"
                )
            result = self._kserve.predict(feature_values, customer_id)
            return result
        except CustomerNotFoundError:
            raise
        except Exception as e:
            raise PredictionError(f"Prediction failed: {e}") from e

    def batch_predict(self, customer_ids: list[str]) -> list[dict]:
        results: list[dict] = []
        for customer_id in customer_ids:
            try:
                results.append(self.predict(customer_id))
            except (CustomerNotFoundError, PredictionError):
                results.append(
                    {"customer_id": customer_id, "error": "prediction_failed"}
                )
        return results
