# Architecture Overview

## Purpose

This document describes the end-to-end architecture of the customer attrition (churn)
MLOps platform: how data becomes features, how features become a model, how a model
becomes a live prediction service, and how each piece is observed in production.

Read this document before making any change that touches more than one component.
Component-specific detail lives in the linked docs below; this page only covers how
the pieces fit together.

## System diagram

```
                              Airflow Orchestrator
                                      │
             ┌────────────────────────┼────────────────────────┐
             ▼                        ▼                        ▼
      Data Pipeline            Train Pipeline            Deploy Pipeline
   Ingestion→Validation→   Feast Retrieval→Training→   Load Model→
   Preprocessing→Feature   Model→Evaluate               Deploy KServe
   Engineering                       │                        │
             │                       ▼                        │
             ▼                   MLflow                       │
      S3 Data Lake          Tracking / Registry /              │
   (Feast Offline Store)       Artifact store                 │
             ▲───────────────────────┘                        │
                                                                ▼
   Client → FastAPI Backend → Feast Online SDK → Redis   ◄──  KServe
                            → KServe (inference)   ────────────┘
                                      │
                                      ▼
                            Datadog Monitoring
```

See `docs/data-flow.md` for the fully annotated version of this diagram and the
reasoning behind each connection.

## Components and their single responsibility

| Component | Responsibility | Must NOT do |
|---|---|---|
| **Airflow** | Schedule and sequence the three pipelines (Data, Train, Deploy) | Contain business logic |
| **Data Pipeline** | Turn raw customer data into feature tables in S3 | Train or evaluate models |
| **Feast** | Define features, serve historical data for training, serve online data for inference | Perform ETL |
| **S3** | Store raw data, processed data, feature tables, and MLflow artifacts | — |
| **Train Pipeline** | Train and evaluate a candidate model, log it to MLflow | Deploy anything |
| **MLflow** | Track experiments and hold the model registry | Serve predictions |
| **Deploy Pipeline** | Load a registered model and publish it via KServe | Handle live traffic directly |
| **KServe** | Run model inference | Own application/business logic |
| **FastAPI Backend** | Application entry point; orchestrates Feast + KServe calls per request | Talk to Redis or Feast directly from route handlers (must go through a service layer) |
| **Redis** | Low-latency online feature store (Feast online store only) | General-purpose cache |
| **PostgreSQL** | Metadata store for Airflow, MLflow, and the FastAPI application DB | Store raw data, features, or model artifacts |
| **Datadog** | Collect logs, traces, and metrics from the runtime path | — |

## Core architecture principles

1. **Loose coupling between pipelines.** Data Pipeline, Train Pipeline, and Deploy
   Pipeline never call each other directly. They communicate only through shared
   storage: S3 (offline data) and the MLflow Model Registry. This means each
   pipeline can be re-run independently without knowing whether the others succeeded.

2. **Batch vs runtime separation.** Everything under Airflow is batch/scheduled.
   The path from `Client` to `Prediction` is a synchronous, low-latency runtime path
   that Airflow does not control and is not aware of.

3. **Single point of entry to inference.** All prediction requests go through
   FastAPI. Nothing outside FastAPI calls KServe or the Feast online store directly.
   This keeps auth, logging, and request tracing in one place.

4. **Everything that serves live traffic is observed.** FastAPI and KServe emit
   logs, traces, and metrics to Datadog. See `docs/observability.md`.

## Where to look next

- Data movement in detail → `docs/data-flow.md`
- Feature definitions and the online/offline split → `docs/feature-store.md`
- How a model goes from trained to serving → `docs/model-lifecycle.md`
- How KServe and Kubernetes are configured → `docs/deployment.md`
- How the system is monitored → `docs/observability.md`
- Why each major technology was chosen → `docs/adr/`