import sys
from pathlib import Path

import pytest

FEAST_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FEAST_DIR))

feast = pytest.importorskip("feast")
redis = pytest.importorskip("redis")


def test_feature_store_yaml_exists():
    path = FEAST_DIR / "feature_store.yaml"
    assert path.exists(), "feature_store.yaml must be present for feast apply"


def test_feature_views_define_entity_key():
    from feast import FeatureStore

    store = FeatureStore(repo_path=str(FEAST_DIR))
    views = store.list_feature_views()
    assert views, "at least one feature view must be defined"
    for view in views:
        assert view.entities, f"feature view {view.name} must declare entities"
