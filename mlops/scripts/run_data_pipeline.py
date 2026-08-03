import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from customer_attrition.common.config import config
from customer_attrition.common.logging import setup_logging
from customer_attrition.features.build_features import build_features
from customer_attrition.ingestion.load_s3 import load_raw_data
from customer_attrition.ingestion.save_s3 import save_features, save_processed_data
from customer_attrition.preprocessing.clean import clean_data
from customer_attrition.preprocessing.encode import encode_features
from customer_attrition.preprocessing.split import split_data
from customer_attrition.validation.data_quality import run_validation


def main():
    logger = setup_logging()
    logger.info("Starting data pipeline")

    df = load_raw_data(config.s3_bucket, f"{config.s3_raw_prefix}/churn_full.csv")

    run_validation(df)

    df = clean_data(df)
    save_processed_data(
        df, config.s3_bucket, f"{config.s3_processed_prefix}/cleaned.parquet"
    )

    df_encoded = encode_features(df)
    split_data(
        df_encoded,
        config.target_col,
        config.test_size,
        config.val_size,
        config.model_random_state,
    )

    features_df = build_features(df)
    save_features(
        features_df,
        config.s3_bucket,
        f"{config.s3_features_prefix}/churn_features.parquet",
    )

    logger.info("Data pipeline complete")


if __name__ == "__main__":
    main()
