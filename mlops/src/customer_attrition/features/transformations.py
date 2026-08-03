import pandas as pd

from customer_attrition.common.constants import (
    ANNUAL_INCOME,
    DAYS_SINCE_LAST_INTERACTION,
    MONTHLYCHARGES,
    NUM_COMPLAINTS,
    NUM_SERVICES,
    TENURE,
)


def compute_tenure_risk(tenure: pd.Series) -> pd.Series:
    return pd.cut(
        tenure,
        bins=[-1, 6, 12, float("inf")],
        labels=["high", "medium", "low"],
    )


def compute_engagement_score(df: pd.DataFrame) -> pd.Series:
    return (1 / (df[DAYS_SINCE_LAST_INTERACTION] + 1)) * df[NUM_SERVICES]


def compute_complaint_ratio(df: pd.DataFrame) -> pd.Series:
    return df[NUM_COMPLAINTS] / (df[TENURE] + 1)


def compute_spend_to_income_ratio(df: pd.DataFrame) -> pd.Series:
    return df[MONTHLYCHARGES] / (df[ANNUAL_INCOME] + 1)
