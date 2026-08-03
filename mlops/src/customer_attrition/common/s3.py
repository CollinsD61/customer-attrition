import os
from io import BytesIO

import pandas as pd


def _get_session():
    import boto3

    profile = os.getenv("AWS_PROFILE")
    if profile:
        return boto3.Session(profile_name=profile)
    return boto3.Session()


def _get_client():
    from botocore.config import Config as BotoConfig

    return _get_session().client("s3", config=BotoConfig(retries={"max_attempts": 3}))


def read_csv(bucket: str, key: str) -> pd.DataFrame:
    client = _get_client()
    response = client.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(response["Body"])


def write_parquet(df: pd.DataFrame, bucket: str, key: str) -> None:
    buffer = BytesIO()
    df.to_parquet(buffer, engine="pyarrow", index=False)
    client = _get_client()
    client.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())


def read_parquet(bucket: str, key: str) -> pd.DataFrame:
    client = _get_client()
    response = client.get_object(Bucket=bucket, Key=key)
    return pd.read_parquet(BytesIO(response["Body"].read()), engine="pyarrow")


def list_keys(bucket: str, prefix: str) -> list[str]:
    client = _get_client()
    paginator = client.get_paginator("list_objects_v2")
    keys: list[str] = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])
    return keys
