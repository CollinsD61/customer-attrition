import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION") != "1",
    reason="requires live MLflow server; set RUN_INTEGRATION=1",
)


def test_registered_model_version_exists():
    import mlflow

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    client = mlflow.tracking.MlflowClient()
    versions = client.search_model_versions("name='churn-predictor'")
    assert versions, "churn-predictor must have at least one registered version"
