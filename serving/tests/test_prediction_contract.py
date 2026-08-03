import pytest


class FakeModel:
    def predict(self, payload):
        return {"churn_probability": 0.85, "prediction": 1, "model_version": "v2.1"}


@pytest.fixture
def model():
    return FakeModel()


def test_prediction_response_has_model_version(model):
    response = model.predict({})
    assert "model_version" in response


def test_prediction_schema(model):
    response = model.predict({})
    assert 0 <= response["churn_probability"] <= 1
    assert response["prediction"] in (0, 1)
    assert isinstance(response["model_version"], str)
