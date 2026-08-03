import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION") != "1",
    reason="requires live S3 bucket; set RUN_INTEGRATION=1",
)


def test_features_exist_in_s3():
    import boto3

    bucket = os.getenv("S3_BUCKET", "customer-churn-mlops-dev")
    s3 = boto3.client("s3")
    keys = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix="features/"):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])
    assert any("churn_features.parquet" in k for k in keys)
