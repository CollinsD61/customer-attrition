import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from customer_attrition.common.config import config
from customer_attrition.common.logging import setup_logging
from customer_attrition.common.s3 import read_parquet
from customer_attrition.features.build_features import build_features
from customer_attrition.ingestion.save_s3 import save_features


def main() -> None:
    logger = setup_logging()
    df = read_parquet(config.s3_bucket, f"{config.s3_processed_prefix}/cleaned.parquet")
    features_df = build_features(df)
    save_features(
        features_df,
        config.s3_bucket,
        f"{config.s3_features_prefix}/churn_features.parquet",
    )
    logger.info(f"Features built: {len(features_df)} rows")


if __name__ == "__main__":
    main()
