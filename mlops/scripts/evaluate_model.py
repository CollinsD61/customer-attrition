import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import mlflow
from customer_attrition.common.config import config
from customer_attrition.common.logging import setup_logging
from customer_attrition.common.s3 import read_parquet
from customer_attrition.training.evaluate import evaluate_model
from sklearn.model_selection import train_test_split


def main() -> None:
    logger = setup_logging()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    df = read_parquet(
        config.s3_bucket, f"{config.s3_features_prefix}/churn_features.parquet"
    )
    feature_cols = [
        c for c in df.columns if c not in ("customer_id", "signup_date", "churn")
    ]
    X = df[feature_cols]
    y = df["churn"]
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=config.test_size, random_state=config.model_random_state
    )

    model = mlflow.lightgbm.load_model("models:/churn-predictor/Staging")
    metrics = evaluate_model(model, X_test, y_test)
    logger.info(f"Evaluation metrics: {metrics}")


if __name__ == "__main__":
    main()
