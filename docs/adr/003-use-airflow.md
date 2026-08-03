# ADR 003: Use Airflow for Pipeline Orchestration

## Status

Accepted

## Context

Three distinct batch workflows need scheduling, dependency management, retries,
and observability of run history: the Data Pipeline, Train Pipeline, and Deploy
Pipeline. These pipelines are loosely coupled (they communicate only through S3
and the MLflow Model Registry — see `docs/architecture.md`), but each internally
needs a reliable way to sequence steps and recover from partial failures.

## Decision

Use **Airflow** as the orchestrator for all three pipelines. Airflow's
responsibility is strictly scheduling, sequencing, retries, and surfacing run
status — it must never contain business logic. All actual logic (ingestion,
validation, training, deployment steps) lives in
`mlops/src/customer_attrition/`, and DAG files only call into it.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| Cron + shell scripts | No dependency graph, no retry/backfill support, no UI for run history — doesn't scale past a handful of jobs |
| Prefect | Comparable modern alternative; Airflow was chosen for its larger ecosystem of provider integrations (including the Datadog provider used for pipeline observability) and broader team familiarity |
| Dagster | Strong option, especially for its asset-centric model; not chosen to avoid re-deriving the S3/MLflow-centric data contracts we already use as the "asset" boundary |
| Kubernetes CronJobs directly | No cross-task dependency graph within a pipeline; each pipeline is more than a single job |

## Consequences

- DAG files must stay thin (rule enforced in AGENTS.md and `docs/architecture.md`)
  — reviewers should reject PRs that put real logic in a DAG file.
- Airflow needs its own metadata database (`airflow_db` in PostgreSQL — see ADR
  006) to track DAG runs, task state, and connections.
- Task-level logs and metrics can be forwarded to Datadog via the Airflow
  provider, keeping pipeline observability consistent with the rest of the
  system (see `docs/observability.md`).