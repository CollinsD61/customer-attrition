import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from customer_attrition.common.config import config
from customer_attrition.common.logging import setup_logging
from customer_attrition.common.s3 import read_parquet
from customer_attrition.training.evaluate import evaluate_model, get_feature_importance
from customer_attrition.training.register import register_model
from customer_attrition.training.train import train_model
from sklearn.model_selection import train_test_split


def main() -> None:
    logger = setup_logging()
    logger.info("Starting training pipeline")

    df = read_parquet(
        config.s3_bucket, f"{config.s3_features_prefix}/churn_features.parquet"
    )
    logger.info(f"Loaded {len(df)} rows from feature store")

    feature_cols = [
        c for c in df.columns if c not in ("customer_id", "signup_date", "churn")
    ]
    X = df[feature_cols]
    y = df["churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.test_size, random_state=config.model_random_state
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train,
        y_train,
        test_size=config.val_size / (1 - config.test_size),
        random_state=config.model_random_state,
    )

    model, _ = train_model(X_train, y_train, X_val, y_val)

    metrics = evaluate_model(model, X_test, y_test)
    logger.info(f"Metrics: {metrics}")

    importance = get_feature_importance(model, feature_cols)
    logger.info(f"Top 5 features: {importance[:5]}")

    version = register_model(
        model, metrics, config.mlflow_experiment_name, "churn-predictor"
    )
    logger.info(f"Model registered: {version}")


if __name__ == "__main__":
    main()
