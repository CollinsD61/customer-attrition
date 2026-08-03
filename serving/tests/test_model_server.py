class FakeFeatureClient:
    def get_online_features(self, customer_id: str) -> dict:
        return {"tenure": 12, "monthlycharges": 70.0, "customer_satisfaction": 5.0}

    def get_feature_vector(self, customer_id: str) -> list:
        return [12, 70.0, 5.0]


class FakeChurnModel:
    model_version = "v2.1"

    def predict(self, features: dict) -> dict:
        return {
            "churn_probability": 0.42,
            "prediction": 0,
            "model_version": self.model_version,
        }


def test_predict_returns_expected_keys():
    model = FakeChurnModel()
    result = model.predict(FakeFeatureClient().get_online_features("C1"))
    assert set(result) == {"churn_probability", "prediction", "model_version"}


def test_feature_client_returns_scalars():
    features = FakeFeatureClient().get_online_features("C1")
    assert isinstance(features["tenure"], int)
    assert isinstance(features["monthlycharges"], float)


def test_prediction_version_traces_to_run():
    model = FakeChurnModel()
    assert model.predict({})["model_version"] == model.model_version
