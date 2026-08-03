import pandas as pd

from customer_attrition.common.constants import CHURN, CUSTOMER_ID, SIGNUP_DATE, TENURE
from customer_attrition.features.feature_schema import FEATURE_COLUMNS
from customer_attrition.features.transformations import (
    compute_complaint_ratio,
    compute_engagement_score,
    compute_spend_to_income_ratio,
    compute_tenure_risk,
)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if SIGNUP_DATE in df.columns and not pd.api.types.is_datetime64_any_dtype(
        df[SIGNUP_DATE]
    ):
        df[SIGNUP_DATE] = pd.to_datetime(df[SIGNUP_DATE], utc=True)

    df["tenure_risk"] = compute_tenure_risk(df[TENURE])
    df["engagement_score"] = compute_engagement_score(df)
    df["complaint_ratio"] = compute_complaint_ratio(df)
    df["spend_to_income_ratio"] = compute_spend_to_income_ratio(df)

    id_cols = [CUSTOMER_ID, SIGNUP_DATE]
    feature_cols = [c for c in FEATURE_COLUMNS if c in df.columns]
    engineered = [
        "tenure_risk",
        "engagement_score",
        "complaint_ratio",
        "spend_to_income_ratio",
    ]
    all_cols = id_cols + feature_cols + engineered + [CHURN]

    return df[[c for c in all_cols if c in df.columns]]
