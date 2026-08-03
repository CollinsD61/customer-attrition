import os
import sys
from datetime import UTC, datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from airflow import DAG
from airflow.operators.python import PythonOperator
from customer_attrition.common.logging import setup_logging
from feast import FeatureStore

_FEAST_REPO = os.path.join(os.path.dirname(__file__), "..", "..", "feast")


def _materialize_features(**context) -> None:
    logger = setup_logging()
    store = FeatureStore(repo_path=_FEAST_REPO)
    store.materialize(
        start_date=datetime.now(tz=UTC),
        end_date=datetime.now(tz=UTC),
    )
    logger.info("Materialization complete")


default_args = {
    "owner": "mlops",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="materialize_features",
    default_args=default_args,
    description="Hourly feature materialization to Redis online store",
    schedule_interval="@hourly",
    start_date=datetime(2025, 1, 1, tzinfo=UTC),
    catchup=False,
    tags=["customer-attrition", "feast"],
) as dag:
    materialize_features = PythonOperator(
        task_id="materialize_features",
        python_callable=_materialize_features,
    )
