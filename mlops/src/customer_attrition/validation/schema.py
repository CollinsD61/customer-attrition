import pandas as pd

from customer_attrition.common.constants import (
    AGE,
    ANNUAL_INCOME,
    AVG_MONTHLY_GB,
    CHURN,
    CONTRACT,
    CREDIT_SCORE,
    CUSTOMER_ID,
    CUSTOMER_SATISFACTION,
    DAYS_SINCE_LAST_INTERACTION,
    DEPENDENTS,
    EDUCATION,
    GENDER,
    HAS_DEVICE_PROTECTION,
    HAS_INTERNET_SERVICE,
    HAS_ONLINE_BACKUP,
    HAS_ONLINE_SECURITY,
    HAS_PHONE_SERVICE,
    HAS_STREAMING_MOVIES,
    HAS_STREAMING_TV,
    HAS_TECH_SUPPORT,
    LATE_PAYMENTS,
    MARITAL_STATUS,
    MONTHLYCHARGES,
    NUM_COMPLAINTS,
    NUM_SERVICE_CALLS,
    NUM_SERVICES,
    PAPERLESS_BILLING,
    PAYMENT_METHOD,
    SENIOR_CITIZEN,
    SIGNUP_DATE,
    TENURE,
    TOTALCHARGES,
)

EXPECTED_COLUMNS = [
    CUSTOMER_ID,
    SIGNUP_DATE,
    AGE,
    GENDER,
    ANNUAL_INCOME,
    EDUCATION,
    MARITAL_STATUS,
    DEPENDENTS,
    TENURE,
    CONTRACT,
    PAYMENT_METHOD,
    PAPERLESS_BILLING,
    SENIOR_CITIZEN,
    MONTHLYCHARGES,
    TOTALCHARGES,
    NUM_SERVICES,
    HAS_PHONE_SERVICE,
    HAS_INTERNET_SERVICE,
    HAS_ONLINE_SECURITY,
    HAS_ONLINE_BACKUP,
    HAS_DEVICE_PROTECTION,
    HAS_TECH_SUPPORT,
    HAS_STREAMING_TV,
    HAS_STREAMING_MOVIES,
    CUSTOMER_SATISFACTION,
    NUM_COMPLAINTS,
    NUM_SERVICE_CALLS,
    LATE_PAYMENTS,
    AVG_MONTHLY_GB,
    DAYS_SINCE_LAST_INTERACTION,
    CREDIT_SCORE,
    CHURN,
]

EXPECTED_TYPES: dict[str, type] = {
    CUSTOMER_ID: object,
    SIGNUP_DATE: object,
    AGE: int,
    GENDER: object,
    ANNUAL_INCOME: float,
    EDUCATION: object,
    MARITAL_STATUS: object,
    DEPENDENTS: int,
    TENURE: int,
    CONTRACT: object,
    PAYMENT_METHOD: object,
    PAPERLESS_BILLING: object,
    SENIOR_CITIZEN: object,
    MONTHLYCHARGES: float,
    TOTALCHARGES: float,
    NUM_SERVICES: int,
    HAS_PHONE_SERVICE: object,
    HAS_INTERNET_SERVICE: object,
    HAS_ONLINE_SECURITY: object,
    HAS_ONLINE_BACKUP: object,
    HAS_DEVICE_PROTECTION: object,
    HAS_TECH_SUPPORT: object,
    HAS_STREAMING_TV: object,
    HAS_STREAMING_MOVIES: object,
    CUSTOMER_SATISFACTION: int,
    NUM_COMPLAINTS: int,
    NUM_SERVICE_CALLS: int,
    LATE_PAYMENTS: int,
    AVG_MONTHLY_GB: float,
    DAYS_SINCE_LAST_INTERACTION: int,
    CREDIT_SCORE: float,
    CHURN: int,
}


def validate_schema(df: pd.DataFrame) -> tuple[bool, list[str]]:
    errors: list[str] = []

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")

    extra = [c for c in df.columns if c not in EXPECTED_COLUMNS]
    if extra:
        errors.append(f"Unexpected columns: {extra}")

    if missing or extra:
        return False, errors

    for col, expected_type in EXPECTED_TYPES.items():
        if col in df.columns and not pd.api.types.is_object_dtype(df[col]):
            actual = df[col].dtype
            if expected_type is int:
                if pd.api.types.is_integer_dtype(actual):
                    continue
                if pd.api.types.is_float_dtype(actual):
                    non_null = df[col].dropna()
                    if non_null.eq(non_null.astype("Int64")).all():
                        continue
                errors.append(f"Column '{col}' expected int, got {actual}")
            elif expected_type is float and not pd.api.types.is_float_dtype(actual):
                errors.append(f"Column '{col}' expected float, got {actual}")

    return len(errors) == 0, errors
