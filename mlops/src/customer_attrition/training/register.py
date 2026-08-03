import mlflow
import mlflow.lightgbm


def register_model(
    model,
    metrics: dict,
    experiment_name: str,
    model_name: str,
    artifact_path: str = "model",
) -> str:
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run() as run:
        mlflow.log_metrics(metrics)
        mlflow.lightgbm.log_model(model, artifact_path=artifact_path)
        result = mlflow.register_model(
            f"runs:/{run.info.run_id}/{artifact_path}",
            model_name,
        )
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=model_name,
            version=result.version,
            stage="Staging",
        )
    return str(result.version)
