# ADR 006: Use a Single PostgreSQL Instance for Structured Metadata

## Status

Accepted

## Context

Several components need a relational database for structured metadata that
doesn't belong in S3 (large files) or Redis (ephemeral low-latency lookups):

- **Airflow** needs a metadata database for DAG run history, task instance
  state, connections, and variables.
- **MLflow** needs a backend store for experiment runs, parameters, metrics,
  and model registry entries (see ADR 005).
- The **FastAPI application** needs a database for its own business data:
  customer records, prediction request logs, and user/auth data.
- **Feast** optionally needs a registry backend if feature definitions are
  edited concurrently by multiple people or pipelines.

Each of these is logically separate — they have different owners, different
access patterns, and no reason to share a schema.

## Decision

Run **one PostgreSQL instance**, with a **separate logical database per
consumer**:

| Database | Owner | Stores |
|---|---|---|
| `airflow_db` | Airflow | DAG runs, task instance states, connections/variables, schedules |
| `mlflow_db` | MLflow | Experiments, runs, params, metrics, model registry metadata, tags |
| `app_db` | FastAPI Backend | customer, prediction, user tables (application's own migrations) |
| `feast_db` (optional) | Feast | Feature view definitions, feature services, data source configs — only needed if the file-based registry on S3 becomes a bottleneck |

`airflow_db` and `mlflow_db` are internal databases owned and migrated by their
respective tools — application code should never write to them directly.
`app_db` is owned by the FastAPI codebase and migrated via its own
`db/migrations/` — this is the only one of the four that application code
queries directly.

One instance rather than four separate ones keeps operational overhead low,
which matters most for local (`kind`) development; each database can still be
split onto its own managed instance later without any application code change,
since each consumer already treats its database as logically isolated.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| Four separate PostgreSQL instances | Unnecessary operational overhead at current scale; nothing about the architecture requires physical isolation, only logical isolation |
| SQLite for Airflow/MLflow (their defaults) | Not safe for concurrent access or production-like usage; fine for a five-minute demo, not for this project |
| A shared database (single schema) for everything | Couples unrelated tools' schemas together; a migration in one tool could accidentally collide with another's tables |

## Consequences

- One PostgreSQL pod/service to run in `k8s/`, with four database names created
  at provisioning time.
- Credentials must be scoped per database (Airflow's user should not be able to
  write to `app_db`, and vice versa) — do not commit real credentials; use
  `k8s/secrets.example.yaml` as the template (see `docs/security.md`).
- `feast_db` starts unused; only provision it if/when the file-based registry
  becomes a concurrency bottleneck (see `docs/feature-store.md`).