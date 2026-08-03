import pandas as pd

from customer_attrition.common.constants import (
    CONTRACT,
    EDUCATION,
    GENDER,
    MARITAL_STATUS,
    PAYMENT_METHOD,
)

_ENCODE_COLS = [CONTRACT, PAYMENT_METHOD, GENDER, EDUCATION, MARITAL_STATUS]


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in _ENCODE_COLS:
        if col in df.columns:
            dummies = pd.get_dummies(df[col], prefix=col, drop_first=True, dtype=int)
            df = pd.concat([df, dummies], axis=1)
            df = df.drop(columns=[col])

    return df
