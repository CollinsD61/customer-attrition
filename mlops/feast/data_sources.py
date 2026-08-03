from feast import FileSource
from feast.data_format import ParquetFormat

churn_features_source = FileSource(
    name="churn_features_source",
    path="s3://customer-churn-mlops-dev/features/churn_features.parquet",
    timestamp_field="signup_date",
    file_format=ParquetFormat(),
)
