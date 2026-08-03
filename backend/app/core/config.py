from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "RetentionPulse API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    FEAST_REGISTRY_PATH: str = "s3://customer-churn-mlops-dev/feast/registry.db"
    KSERVE_SERVICE_URL: str = "http://churn-predictor.default.svc.cluster.local/v1/models/churn-predictor:predict"
    KSERVE_MODEL_NAME: str = "churn-predictor"
    DATABASE_URL: str = (
        "postgresql://postgres:postgres@localhost:5432/customer_attrition"
    )
    SECRET_KEY: str = "change-me-in-production"
    AWS_PROFILE: str | None = None

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
