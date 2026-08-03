# Data Flow

This document walks through every hop data takes in the system, in order, and
states which component is responsible for each hop. Read `docs/architecture.md`
first for the component overview.

## 1. Batch: Data Pipeline

Triggered by Airflow on a schedule.

1. **Ingestion** (`mlops/src/customer_attrition/ingestion/`) pulls raw customer
   data from source systems.
2. **Validation** (`.../validation/`) checks schema, null rates, and value ranges.
   A failed validation stops the DAG — bad data never reaches preprocessing.
3. **Preprocessing** (`.../preprocessing/`) cleans and joins raw sources into a
   unified table.
4. **Feature engineering** (`.../features/`) computes the churn-relevant features
   (tenure, usage trend, support ticket count, etc.).
5. Output is written to **S3 Data Lake**, which acts as the Feast **offline store**.
   S3 holds three logical layers: raw data, processed data, and feature tables.

Data Pipeline never talks to Feast, MLflow, or KServe. Its only external contract
is: *whatever it writes to S3 must match the feature schema Feast expects.*

## 2. Batch: Train Pipeline

Triggered by Airflow, independently of when Data Pipeline last ran (it uses
whatever is currently in S3).

1. **Feast historical retrieval**: given an entity dataframe (customer_id +
   event_timestamp + churn label, sourced separately from the label table — Feast
   does not generate labels), Feast performs a point-in-time join against the S3
   offline store to build a leakage-free training set.
2. **Training dataset** is the joined output.
3. **Train model** fits the churn classifier.
4. **Evaluate** computes metrics (AUC, F1, precision/recall) on a held-out set.
5. **MLflow** receives the run: parameters, metrics, and the model artifact are
   logged via **Tracking**; if the run passes the evaluation bar it is promoted to
   the **Model Registry**. The artifact itself is stored back in S3 (`Artifact store`).

Train Pipeline reads from S3 and writes to MLflow. It never touches KServe or the
application backend.

## 3. Batch: Deploy Pipeline

Triggered when a new model version is promoted in the registry (manually or via
an Airflow sensor watching the registry).

1. **Load model**: pull the registered model version from MLflow.
2. **Deploy KServe**: package it and publish it as a KServe `InferenceService`.

This is a deploy-time action, not a runtime call — it creates or updates the
running inference service; it does not itself serve any request.

## 4. Runtime: Online serving (not orchestrated by Airflow)

This path runs continuously, independent of the batch pipelines above.

1. **Client** sends a prediction request to the **FastAPI Backend**.
2. FastAPI's service layer (never the route handler directly) calls the
   **Feast Online SDK**, which reads the latest materialized features from
   **Redis**.
3. FastAPI passes those features to **KServe** via `backend/app/services/kserve_client.py`.
4. **KServe** runs inference and returns a prediction, including the model version.
5. FastAPI returns the response to the Client.
6. FastAPI and KServe emit logs/traces/metrics to **Datadog** throughout.

Order matters: features must be fetched **before** the KServe call — a prediction
cannot be made without them.

## 5. Materialize job (connects batch to runtime)

A separate, independently scheduled job (not part of Train Pipeline) keeps Redis in
sync with S3:

```
S3 offline store → Feast materialize → Redis online store
```

Run cadence should match how quickly churn features go stale (e.g. hourly). See
`docs/feature-store.md` for details.

## Summary table

| From | To | Mechanism | Nature |
|---|---|---|---|
| Data Pipeline | S3 | Batch write | Data |
| S3 | Train Pipeline | Feast historical retrieval | Data |
| Train Pipeline | MLflow | Tracking API | Metadata |
| MLflow | S3 | Artifact store | Data |
| MLflow (Registry) | Deploy Pipeline | Model load | Metadata |
| Deploy Pipeline | KServe | Service creation | Infra (deploy-time) |
| S3 | Redis | Feast materialize | Data (scheduled) |
| Client | FastAPI | HTTP request | Runtime |
| FastAPI | Redis (via Feast SDK) | Feature lookup | Runtime |
| FastAPI | KServe | Inference call | Runtime |
| FastAPI, KServe | Datadog | Telemetry | Observability |