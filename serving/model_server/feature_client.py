from feast import FeatureStore


class FeatureClient:
    def __init__(self, repo_path: str) -> None:
        self._store = FeatureStore(repo_path=repo_path)

    def get_online_features(
        self, customer_id: str, feature_service_name: str = "churn_feature_service"
    ) -> dict:
        feature_service = self._store.get_feature_service(feature_service_name)
        entity_rows = [{"customer_id": customer_id}]
        response = self._store.get_online_features(
            features=feature_service,
            entity_rows=entity_rows,
        )

        result: dict = {}
        for feature_name, values in response.to_dict().items():
            result[feature_name] = values[0] if values else None
        return result

    def get_feature_vector(self, customer_id: str) -> list:
        features = self.get_online_features(customer_id)
        return [features[name] for name in features if name not in ("customer_id",)]
