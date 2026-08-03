import pandas as pd

from customer_attrition.common.constants import (
    CHURN,
    CUSTOMER_ID,
    CUSTOMER_SATISFACTION,
    MONTHLYCHARGES,
    TENURE,
)


def validate_values(df: pd.DataFrame) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if df[CUSTOMER_ID].isnull().any():
        errors.append(f"'{CUSTOMER_ID}' contains null values")

    if df[CHURN].isnull().any():
        errors.append(f"'{CHURN}' contains null values")

    if not df[CHURN].isin([0, 1]).all():
        errors.append(f"'{CHURN}' contains values outside {{0, 1}}")

    if (df[TENURE].dropna() < 0).any():
        errors.append(f"'{TENURE}' contains negative values")

    if (df[MONTHLYCHARGES].dropna() <= 0).any():
        errors.append(f"'{MONTHLYCHARGES}' contains non-positive values")

    if not df[CUSTOMER_SATISFACTION].dropna().between(1, 10).all():
        errors.append(f"'{CUSTOMER_SATISFACTION}' contains values outside [1, 10]")

    return len(errors) == 0, errors
