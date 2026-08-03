import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

os.environ.setdefault("REDIS_CONNECTION", "redis:6379")

from customer_attrition.common.logging import setup_logging
from feast import FeatureStore
from feast.repo_operations import apply_total


def main() -> None:
    logger = setup_logging()
    repo_path = os.path.join(os.path.dirname(__file__), "..", "feast")
    sys.path.insert(0, repo_path)
    store = FeatureStore(repo_path=repo_path)
    apply_total(store.config, Path(repo_path), skip_source_validation=True)
    logger.info("Feast definitions applied")


if __name__ == "__main__":
    main()
