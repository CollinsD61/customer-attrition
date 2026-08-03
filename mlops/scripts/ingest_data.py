import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from customer_attrition.common.config import config
from customer_attrition.common.logging import setup_logging
from customer_attrition.ingestion.load_s3 import load_raw_data


def main() -> None:
    logger = setup_logging()
    df = load_raw_data(config.s3_bucket, f"{config.s3_raw_prefix}/churn_full.csv")
    logger.info(f"Ingested {len(df)} rows")


if __name__ == "__main__":
    main()
