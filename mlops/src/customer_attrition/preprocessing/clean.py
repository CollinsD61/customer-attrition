import pandas as pd

from customer_attrition.common.constants import (
    BOOLEAN_COLS,
    CUSTOMER_ID,
    PAPERLESS_BILLING,
    SENIOR_CITIZEN,
)
from customer_attrition.validation.schema import EXPECTED_TYPES

_BOOL_MAP = {"Yes": 1, "No": 0}


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=[CUSTOMER_ID])

    for col, expected_type in EXPECTED_TYPES.items():
        if col not in df.columns or df[col].dtype == object:
            continue
        if expected_type is int and pd.api.types.is_integer_dtype(df[col]):
            continue
        if not df[col].isna().any():
            continue
        df[col] = df[col].fillna(df[col].median())
        if expected_type is int:
            df[col] = df[col].round().astype("int64")

    for col in BOOLEAN_COLS:
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].map(_BOOL_MAP).fillna(0).astype(int)

    if PAPERLESS_BILLING in df.columns and df[PAPERLESS_BILLING].dtype == object:
        df[PAPERLESS_BILLING] = (
            df[PAPERLESS_BILLING].map(_BOOL_MAP).fillna(0).astype(int)
        )

    if SENIOR_CITIZEN in df.columns and df[SENIOR_CITIZEN].dtype == object:
        df[SENIOR_CITIZEN] = df[SENIOR_CITIZEN].map(_BOOL_MAP).fillna(0).astype(int)

    return df
