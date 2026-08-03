from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MODEL_NAME: str = "churn-predictor"
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    FEAST_REGISTRY_PATH: str = "s3://customer-churn-mlops-dev/feast/registry.db"
    S3_BUCKET: str = "customer-churn-mlops-dev"
    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
