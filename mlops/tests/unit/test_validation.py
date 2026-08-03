import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "mlops" / "src"))

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "sample_churn.csv"

from customer_attrition.common.constants import CHURN, CUSTOMER_ID
from customer_attrition.validation.data_quality import run_validation
from customer_attrition.validation.expectations import validate_values
from customer_attrition.validation.schema import validate_schema


@pytest.fixture
def valid_df() -> pd.DataFrame:
    return pd.read_csv(FIXTURE)


def test_validate_schema_accepts_valid_data(valid_df):
    ok, errors = validate_schema(valid_df)

    assert ok is True
    assert errors == []


def test_validate_schema_rejects_missing_column(valid_df):
    df = valid_df.drop(columns=[CHURN])

    ok, errors = validate_schema(df)

    assert ok is False
    assert any("Missing columns" in error for error in errors)
    assert any(CHURN in error for error in errors)


def test_validate_values_rejects_null_customer_id(valid_df):
    df = valid_df.copy()
    df.loc[0, CUSTOMER_ID] = None

    ok, errors = validate_values(df)

    assert ok is False
    assert any(CUSTOMER_ID in error and "null" in error.lower() for error in errors)


def test_validate_values_rejects_invalid_churn(valid_df):
    df = valid_df.copy()
    df.loc[0, CHURN] = 2

    ok, errors = validate_values(df)

    assert ok is False
    assert any(CHURN in error for error in errors)


def test_run_validation_raises_on_invalid(valid_df):
    df = valid_df.drop(columns=[CHURN])

    with pytest.raises(ValueError):
        run_validation(df)
