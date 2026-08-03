import sys
import types
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "mlops" / "src"))

# Stub the S3 persistence module so build_features can be imported and run
# without boto3 or a real S3 bucket.
_fake_save_s3 = types.ModuleType("customer_attrition.ingestion.save_s3")


def _save_features(df: pd.DataFrame, bucket: str, key: str) -> None:
    pass


_fake_save_s3.save_features = _save_features
sys.modules["customer_attrition.ingestion.save_s3"] = _fake_save_s3

from customer_attrition.common.constants import CHURN, CUSTOMER_ID, SIGNUP_DATE, TENURE
from customer_attrition.features.build_features import build_features
from customer_attrition.features.feature_schema import FEATURE_COLUMNS
from customer_attrition.features.transformations import compute_tenure_risk


def test_build_features_adds_engineered_columns():
    df = pd.DataFrame(
        {
            CUSTOMER_ID: ["CUST1", "CUST2"],
            SIGNUP_DATE: ["2022-01-01", "2022-01-02"],
            TENURE: [2, 20],
            "days_since_last_interaction": [5, 10],
            "num_services": [3, 4],
            "num_complaints": [1, 0],
            "monthlycharges": [50.0, 100.0],
            "annual_income": [50000.0, 60000.0],
            CHURN: [0, 1],
        }
    )

    out = build_features(df)

    for col in [
        "tenure_risk",
        "engagement_score",
        "complaint_ratio",
        "spend_to_income_ratio",
    ]:
        assert col in out.columns
    assert out.shape[0] == len(df)


def test_compute_tenure_risk_buckets():
    result = compute_tenure_risk(pd.Series([2, 9, 20]))

    assert list(result) == ["high", "medium", "low"]


def test_feature_schema_has_expected_columns():
    assert isinstance(FEATURE_COLUMNS, list)
    assert "tenure" in FEATURE_COLUMNS
