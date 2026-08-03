# Model Lifecycle

This document covers what happens to a model from the moment it's trained to the
moment it's retired.

## Stages

```
Train → Evaluate → Log to MLflow (Tracking) → Register (staging) →
Promote (production) → Load → Deploy to KServe → Serve → Monitor → Retrain / Retire
```

### 1. Train

`mlops/src/customer_attrition/training/`, run via:

```bash
python mlops/scripts/train_model.py
```

Trains on the dataset produced by Feast historical retrieval.

### 2. Evaluate

Every training run is scored against a held-out test set. Minimum bar (adjust as
the project matures):

- AUC and F1 must not regress versus the current production model by more than an
  agreed tolerance.
- Evaluation must run against the **same** feature schema that will be used online
  — a mismatch here is the most common source of training/serving skew.

### 3. Log to MLflow (Tracking)

Every run — successful or not — is logged: parameters, metrics, and the model
artifact. This gives full lineage even for runs that don't get promoted.

### 4. Register

A run that passes evaluation is registered in the MLflow **Model Registry** as a
new version, initially in a non-production stage (e.g. `Staging`).

### 5. Promote

Promotion to `Production` is a deliberate step, not automatic. Before promoting:

- Confirm the model's input/output schema matches what
  `backend/app/services/kserve_client.py` expects.
- Confirm the feature list used in training is currently materialized in Redis
  (a feature that's only in the offline store will silently be missing online).

### 6. Load and deploy

Deploy Pipeline loads the promoted version and publishes it via KServe
(`docs/deployment.md` has the mechanics).

### 7. Serve

KServe returns predictions to FastAPI, which returns them to the client. Every
response includes the model version, so you can always trace a prediction back to
the exact training run that produced it (via MLflow).

### 8. Monitor

Datadog tracks prediction latency, error rate, and (where instrumented) input
feature drift. See `docs/observability.md`.

### 9. Retrain / retire

Retrain when:

- Scheduled retrain cadence is reached (Airflow-triggered), or
- Monitoring shows performance degradation or feature drift, or
- The label distribution has shifted materially (e.g. churn definition changed).

Retire a model version by demoting it in the registry — never delete artifacts;
S3 retains them for audit/rollback.

## Rollback

Because every deployed version is tied to an immutable MLflow registry entry,
rollback is: promote the previous version, re-run Deploy Pipeline. No retraining
needed.

## Testing requirements when changing this stage

- Preserve the input and output schema of the model contract.
- Run prediction contract tests before promoting.
- Include model version in every prediction response.