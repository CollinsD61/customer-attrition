import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

os.environ.setdefault("REDIS_CONNECTION", "redis:6379")

from datetime import UTC, datetime, timedelta

from customer_attrition.common.logging import setup_logging
from feast import FeatureStore


def main() -> None:
    logger = setup_logging()
    logger.info("Starting feature materialization")

    store = FeatureStore(
        repo_path=os.path.join(os.path.dirname(__file__), "..", "feast")
    )
    store.materialize(
        start_date=datetime.now(UTC) - timedelta(days=5 * 365),
        end_date=datetime.now(UTC),
    )
    logger.info("Materialization complete")


if __name__ == "__main__":
    main()
