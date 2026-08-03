import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import mlflow
from customer_attrition.common.config import config
from customer_attrition.common.logging import setup_logging


def main() -> None:
    logger = setup_logging()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    logger.info("Use train_model.py for full training+registration pipeline")


if __name__ == "__main__":
    main()
