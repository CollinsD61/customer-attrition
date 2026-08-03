import os
import sys
from datetime import UTC, datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from airflow import DAG
from airflow.operators.python import PythonOperator
from customer_attrition.common.config import config
from customer_attrition.common.logging import setup_logging

_INFERENCE_YAML = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "..",
    "k8s",
    "kserve",
    "inference-service.yaml",
)


def _check_model_registry(**context) -> None:
    import mlflow

    logger = setup_logging()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    client = mlflow.tracking.MlflowClient()
    versions = client.get_latest_versions("churn-predictor", stages=["Staging"])
    if not versions:
        raise ValueError("No model found in Staging stage")
    logger.info(f"Model version {versions[0].version} ready for deployment")


def _promote_model(**context) -> None:
    import mlflow

    logger = setup_logging()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    client = mlflow.tracking.MlflowClient()
    versions = client.get_latest_versions("churn-predictor", stages=["Staging"])
    if versions:
        client.transition_model_version_stage(
            name="churn-predictor",
            version=versions[0].version,
            stage="Production",
        )
        logger.info(f"Model version {versions[0].version} promoted to Production")


default_args = {
    "owner": "mlops",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def _deploy_to_kserve(**context) -> None:
    import yaml
    from kubernetes import client, config
    
    logger = setup_logging()
    
    config.load_incluster_config()
    api = client.CustomObjectsApi()
    
    # Git sync clones to /opt/airflow/dags/repo
    yaml_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "k8s", "kserve", "inference-service.yaml"
    )
    with open(yaml_path, "r") as f:
        resource = yaml.safe_load(f)
        
    name = resource["metadata"]["name"]
    namespace = resource["metadata"]["namespace"]
    
    try:
        api.create_namespaced_custom_object(
            group="serving.kserve.io",
            version="v1beta1",
            namespace=namespace,
            plural="inferenceservices",
            body=resource,
        )
        logger.info(f"Created InferenceService {name} in {namespace}")
    except client.exceptions.ApiException as e:
        if e.status == 409:
            # Patch existing
            api.patch_namespaced_custom_object(
                group="serving.kserve.io",
                version="v1beta1",
                namespace=namespace,
                plural="inferenceservices",
                name=name,
                body=resource,
            )
            logger.info(f"Updated InferenceService {name} in {namespace}")
        else:
            raise

with DAG(
    dag_id="deploy_pipeline",
    default_args=default_args,
    description="Manual deployment pipeline: check registry, promote model, deploy to KServe",
    schedule=None,
    start_date=datetime(2025, 1, 1, tzinfo=UTC),
    catchup=False,
    tags=["customer-attrition", "deployment"],
) as dag:
    check_model_registry = PythonOperator(
        task_id="check_model_registry",
        python_callable=_check_model_registry,
    )

    promote_model = PythonOperator(
        task_id="promote_model",
        python_callable=_promote_model,
    )

    deploy_to_kserve = PythonOperator(
        task_id="deploy_to_kserve",
        python_callable=_deploy_to_kserve,
    )

    check_model_registry >> promote_model >> deploy_to_kserve
