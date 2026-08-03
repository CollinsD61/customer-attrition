import os
from dataclasses import dataclass, field


@dataclass
class Config:
    s3_bucket: str = field(
        default_factory=lambda: os.getenv("S3_BUCKET", "customer-churn-mlops-dev")
    )
    s3_raw_prefix: str = field(
        default_factory=lambda: os.getenv("S3_RAW_PREFIX", "raw")
    )
    s3_processed_prefix: str = field(
        default_factory=lambda: os.getenv("S3_PROCESSED_PREFIX", "processed")
    )
    s3_features_prefix: str = field(
        default_factory=lambda: os.getenv("S3_FEATURES_PREFIX", "features")
    )
    mlflow_tracking_uri: str = field(
        default_factory=lambda: os.getenv(
            "MLFLOW_TRACKING_URI", "http://localhost:5000"
        )
    )
    mlflow_experiment_name: str = field(
        default_factory=lambda: os.getenv("MLFLOW_EXPERIMENT_NAME", "customer-churn")
    )
    redis_host: str = field(
        default_factory=lambda: os.getenv("REDIS_HOST", "localhost")
    )
    redis_port: int = field(
        default_factory=lambda: int(os.getenv("REDIS_PORT", "6379"))
    )
    feast_registry_path: str = field(
        default_factory=lambda: os.getenv(
            "FEAST_REGISTRY_PATH", "s3://customer-churn-mlops-dev/feast-registry/"
        )
    )
    aws_profile: str | None = field(default_factory=lambda: os.getenv("AWS_PROFILE"))
    model_random_state: int = field(
        default_factory=lambda: int(os.getenv("MODEL_RANDOM_STATE", "42"))
    )
    test_size: float = field(
        default_factory=lambda: float(os.getenv("TEST_SIZE", "0.15"))
    )
    val_size: float = field(
        default_factory=lambda: float(os.getenv("VAL_SIZE", "0.15"))
    )
    target_col: str = field(default_factory=lambda: os.getenv("TARGET_COL", "churn"))


config = Config()
