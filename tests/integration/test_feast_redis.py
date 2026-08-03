import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION") != "1",
    reason="requires live Redis/Feast; set RUN_INTEGRATION=1",
)


def test_feast_online_read_returns_expected_entity():
    from feast import FeatureStore

    repo_path = os.getenv("FEAST_REPO_PATH", "mlops/feast")
    store = FeatureStore(repo_path=repo_path)
    response = store.get_online_features(
        features=["churn_feature_view:tenure"],
        entity_rows=[{"customer_id": "CUST0000000001"}],
    )
    data = response.to_dict()
    assert "tenure" in data
    assert data["tenure"][0] is not None
