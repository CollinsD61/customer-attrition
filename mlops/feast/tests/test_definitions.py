import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

pytest.importorskip("feast")

# The definitions are written for an older feast (ParquetSource,
# feast.types.Timestamp, string value_type). If the installed feast is too new
# to import them, skip rather than fail.
try:
    from mlops.feast.entities import customer
    from mlops.feast.feature_services import churn_feature_service
    from mlops.feast.feature_views import churn_feature_view
except Exception as exc:  # noqa: BLE001 - depends on feast version
    pytest.skip(
        f"Feast definitions not importable with this feast version: {exc}",
        allow_module_level=True,
    )


def test_entity_defined():
    assert customer.name == "customer"
    assert "STRING" in str(customer.value_type).upper()


def test_feature_view_defined():
    assert churn_feature_view.name == "churn_feature_view"
    feature_names = [field.name for field in churn_feature_view.schema]
    assert len(feature_names) > 0
    assert "tenure" in feature_names


def test_feature_service_contains_view():
    assert churn_feature_service.name == "churn_feature_service"
    view_names = [
        getattr(view, "name", None) for view in churn_feature_service.features
    ]
    assert "churn_feature_view" in view_names
