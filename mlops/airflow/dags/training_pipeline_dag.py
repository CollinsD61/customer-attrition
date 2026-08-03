import os
import sys
from datetime import UTC, datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from customer_attrition.common.config import config
from customer_attrition.common.logging import setup_logging
from customer_attrition.common.s3 import read_parquet


_FEATURES_KEY = f"{config.s3_features_prefix}/churn_features.parquet"
_MIN_ROC_AUC = 0.75


def _fetch_training_data(**context) -> None:
    logger = setup_logging()
    df = read_parquet(config.s3_bucket, _FEATURES_KEY)
    feature_cols = [
        c for c in df.columns if c not in ("customer_id", "signup_date", "churn")
    ]
    X = df[feature_cols]
    y = df["churn"]

    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.test_size, random_state=config.model_random_state
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train,
        y_train,
        test_size=config.val_size / (1 - config.test_size),
        random_state=config.model_random_state,
    )

    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    X_val_scaled = scaler.transform(X_val)

    import pickle
    from io import BytesIO

    buffer = BytesIO()
    pickle.dump(
        (
            X_train_scaled,
            X_test_scaled,
            X_val_scaled,
            y_train,
            y_test,
            y_val,
            feature_cols,
        ),
        buffer,
    )
    context["ti"].xcom_push(key="training_data", value=buffer.getvalue().hex())
    logger.info(f"Training data fetched: {len(df)} rows, {len(feature_cols)} features")


def _train_and_evaluate(**context) -> None:
    import pickle
    from io import BytesIO

    logger = setup_logging()
    ti = context["ti"]
    data = pickle.loads(
        bytes.fromhex(ti.xcom_pull(key="training_data", task_ids="fetch_training_data"))
    )
    X_train, X_test, X_val, y_train, y_test, y_val, feature_cols = data

    from customer_attrition.training.evaluate import evaluate_model, get_feature_importance
    from customer_attrition.training.train import train_model

    model, _ = train_model(X_train, y_train, X_val, y_val)
    metrics = evaluate_model(model, X_test, y_test)
    importance = get_feature_importance(model, feature_cols)

    logger.info(f"Metrics: {metrics}")
    logger.info(f"Top 5 features: {importance[:5]}")

    buffer = BytesIO()
    pickle.dump(model, buffer)
    context["ti"].xcom_push(key="model_bytes", value=buffer.getvalue().hex())
    context["ti"].xcom_push(key="metrics", value=metrics)
    context["ti"].xcom_push(key="roc_auc", value=metrics["roc_auc"])


def _check_evaluation(**context) -> bool:
    roc_auc = context["ti"].xcom_pull(key="roc_auc", task_ids="train_and_evaluate")
    if roc_auc < _MIN_ROC_AUC:
        raise ValueError(f"ROC AUC {roc_auc:.4f} below threshold {_MIN_ROC_AUC}")
    return True


def _register_model(**context) -> None:
    import pickle

    logger = setup_logging()
    ti = context["ti"]
    model = pickle.loads(
        bytes.fromhex(ti.xcom_pull(key="model_bytes", task_ids="train_and_evaluate"))
    )
    metrics = ti.xcom_pull(key="metrics", task_ids="train_and_evaluate")
    from customer_attrition.training.register import register_model

    version = register_model(
        model, metrics, config.mlflow_experiment_name, "churn-predictor"
    )
    logger.info(f"Model registered: {version}")


default_args = {
    "owner": "mlops",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="train_pipeline",
    default_args=default_args,
    description="Weekly model training, evaluation, and registration",
    schedule="@weekly",
    start_date=datetime(2025, 1, 1, tzinfo=UTC),
    catchup=False,
    tags=["customer-attrition", "training"],
) as dag:
    fetch_training_data = PythonOperator(
        task_id="fetch_training_data", python_callable=_fetch_training_data
    )
    train_and_evaluate = PythonOperator(
        task_id="train_and_evaluate", python_callable=_train_and_evaluate
    )
    check_evaluation = ShortCircuitOperator(
        task_id="check_evaluation", python_callable=_check_evaluation
    )
    register_model_task = PythonOperator(
        task_id="register_model", python_callable=_register_model
    )

    fetch_training_data >> train_and_evaluate >> check_evaluation >> register_model_task
