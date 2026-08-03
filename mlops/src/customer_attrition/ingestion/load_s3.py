import pandas as pd

from customer_attrition.common.s3 import read_csv as s3_read_csv


def load_raw_data(bucket: str, key: str) -> pd.DataFrame:
    return s3_read_csv(bucket, key)
