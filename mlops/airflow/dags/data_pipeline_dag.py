import os
import sys
from datetime import UTC, datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from airflow import DAG
from airflow.operators.python import PythonOperator
from customer_attrition.common.config import config
from customer_attrition.common.logging import setup_logging
from customer_attrition.common.s3 import read_parquet
from customer_attrition.features.build_features import build_features
from customer_attrition.ingestion.load_s3 import load_raw_data
from customer_attrition.ingestion.save_s3 import save_processed_data
from customer_attrition.preprocessing.clean import clean_data
from customer_attrition.preprocessing.encode import encode_features

_BUCKET = config.s3_bucket
_RAW_KEY = f"{config.s3_raw_prefix}/customer_churn.csv"
_CLEANED_KEY = f"{config.s3_processed_prefix}/cleaned.parquet"
_ENCODED_KEY = f"{config.s3_processed_prefix}/encoded.parquet"
_FEATURES_KEY = f"{config.s3_features_prefix}/churn_features.parquet"


def _ingest_data(**context) -> None:
    logger = setup_logging()
    df = load_raw_data(_BUCKET, _RAW_KEY)
    logger.info(f"Ingested {len(df)} rows")
    context["ti"].xcom_push(key="row_count", value=len(df))


def _validate_data(**context) -> None:
    logger = setup_logging()
    row_count = context["ti"].xcom_pull(key="row_count", task_ids="ingest_data")
    logger.info(f"Validated {row_count} rows")


def _clean_data(**context) -> None:
    logger = setup_logging()
    df = load_raw_data(_BUCKET, _RAW_KEY)
    df = clean_data(df)
    save_processed_data(df, _BUCKET, _CLEANED_KEY)
    logger.info(f"Cleaned: {len(df)} rows")


def _encode_data(**context) -> None:
    logger = setup_logging()
    df = read_parquet(_BUCKET, _CLEANED_KEY)
    df = encode_features(df)
    save_processed_data(df, _BUCKET, _ENCODED_KEY)
    logger.info(f"Encoded: {len(df)} rows")


def _build_features(**context) -> None:
    logger = setup_logging()
    df = read_parquet(_BUCKET, _ENCODED_KEY)
    features_df = build_features(df)
    logger.info(f"Features built: {len(features_df)} rows")


default_args = {
    "owner": "mlops",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="data_pipeline",
    default_args=default_args,
    description="Daily data ingestion, validation, cleaning, encoding, and feature engineering",
    schedule_interval="@daily",
    start_date=datetime(2025, 1, 1, tzinfo=UTC),
    catchup=False,
    tags=["customer-attrition", "data"],
) as dag:
    ingest_data = PythonOperator(task_id="ingest_data", python_callable=_ingest_data)
    validate_data = PythonOperator(
        task_id="validate_data", python_callable=_validate_data
    )
    clean_data_task = PythonOperator(task_id="clean_data", python_callable=_clean_data)
    encode_data_task = PythonOperator(
        task_id="encode_data", python_callable=_encode_data
    )
    build_features_task = PythonOperator(
        task_id="build_features", python_callable=_build_features
    )

    (
        ingest_data
        >> validate_data
        >> clean_data_task
        >> encode_data_task
        >> build_features_task
    )
