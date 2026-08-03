import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "mlops" / "src"))

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "sample_churn.csv"

from customer_attrition.common.constants import (
    CHURN,
    CREDIT_SCORE,
    CUSTOMER_ID,
    PAPERLESS_BILLING,
)
from customer_attrition.preprocessing.clean import clean_data
from customer_attrition.preprocessing.encode import encode_features
from customer_attrition.preprocessing.split import split_data


def test_clean_data_drops_duplicates():
    df = pd.DataFrame(
        {
            CUSTOMER_ID: ["CUST1", "CUST1", "CUST2"],
            "age": [30, 30, 40],
        }
    )

    cleaned = clean_data(df)

    assert len(cleaned) == 2
    assert cleaned[CUSTOMER_ID].nunique() == 2


def test_clean_data_fills_credit_score():
    df = pd.DataFrame(
        {
            CUSTOMER_ID: ["CUST1", "CUST2", "CUST3"],
            CREDIT_SCORE: [600.0, None, 700.0],
        }
    )

    cleaned = clean_data(df)

    assert cleaned[CREDIT_SCORE].isnull().sum() == 0
    filled = cleaned.loc[cleaned[CUSTOMER_ID] == "CUST2", CREDIT_SCORE].iloc[0]
    assert filled == 650.0


def test_clean_data_encodes_booleans():
    df = pd.DataFrame(
        {
            CUSTOMER_ID: ["CUST1", "CUST2"],
            PAPERLESS_BILLING: ["Yes", "No"],
        }
    )

    cleaned = clean_data(df)

    assert cleaned[PAPERLESS_BILLING].tolist() == [1, 0]


def test_encode_features_one_hot_contract():
    df = pd.DataFrame(
        {
            CUSTOMER_ID: ["CUST1", "CUST2", "CUST3"],
            "contract": ["month-to-month", "one_year", "two_year"],
        }
    )

    encoded = encode_features(df)

    # ponytail: get_dummies uses drop_first=True, so the first level
    # ("month-to-month") is the reference and produces no column.
    assert "contract" not in encoded.columns
    assert "contract_one_year" in encoded.columns
    assert "contract_two_year" in encoded.columns


def test_split_data_returns_correct_shapes():
    df = pd.read_csv(FIXTURE)

    X_train, X_val, X_test, y_train, y_val, y_test = split_data(
        df, target_col=CHURN, test_size=0.2, val_size=0.2, random_state=42
    )

    assert len(X_train) == len(y_train)
    assert len(X_val) == len(y_val)
    assert len(X_test) == len(y_test)
    assert len(X_train) + len(X_val) + len(X_test) == len(df)
    assert X_train.shape[1] == df.shape[1] - 1
