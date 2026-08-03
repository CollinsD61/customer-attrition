import pandas as pd

from customer_attrition.common.s3 import write_parquet


def save_processed_data(df: pd.DataFrame, bucket: str, key: str) -> None:
    write_parquet(df, bucket, key)


def save_features(df: pd.DataFrame, bucket: str, key: str) -> None:
    write_parquet(df, bucket, key)
