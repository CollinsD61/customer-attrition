from feast import FeatureStore

from backend.app.core.config import settings
from backend.app.core.exceptions import FeatureLookupError


class FeastClient:
    def __init__(self, repo_path: str | None = None) -> None:
        self._repo_path = repo_path or settings.FEAST_REGISTRY_PATH
        self._store = FeatureStore(repo_path=self._repo_path)

    def get_online_features(self, customer_id: str) -> dict:
        try:
            feature_service = self._store.get_feature_service("churn_feature_service")
            entity_rows = [{"customer_id": customer_id}]
            response = self._store.get_online_features(
                features=feature_service,
                entity_rows=entity_rows,
            )
            result: dict = {}
            for feature_name, values in response.to_dict().items():
                result[feature_name] = values[0] if values else None
            return result
        except Exception as e:
            raise FeatureLookupError(f"Feature lookup failed: {e}") from e

    def get_feature_vector(self, customer_id: str) -> list:
        features = self.get_online_features(customer_id)
        return [features[name] for name in features if name not in ("customer_id",)]
