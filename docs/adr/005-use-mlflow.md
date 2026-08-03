# ADR 005: Use MLflow for Experiment Tracking and Model Registry

## Status

Accepted

## Context

Every training run needs its parameters, metrics, and resulting artifact
recorded so that:

- Model versions are reproducible and auditable (which run produced the model
  currently in production?).
- A model can be promoted from "just trained" to "safe to deploy" through an
  explicit, reviewable step, rather than the Deploy Pipeline picking up whatever
  file happens to be newest in a bucket.
- Deploy Pipeline has a single, unambiguous source of truth for "what is the
  current production model" that is decoupled from Train Pipeline's run
  schedule (see `docs/architecture.md` — pipelines communicate only through
  shared storage/registry, never directly).

## Decision

Use **MLflow** for two distinct responsibilities:

- **Tracking**: log parameters, metrics, tags, and artifacts for every training
  run, successful or not.
- **Model Registry**: hold versioned, named model entries with stage
  transitions (e.g. `Staging` → `Production`), which is what Deploy Pipeline
  reads from.

Structured metadata (run parameters, metrics, registry state) is stored in
**PostgreSQL** (`mlflow_db` — see ADR 006). Large binary artifacts (the model
file itself, plots) are stored in **S3** (see ADR 004), referenced by MLflow but
not stored in the metadata database.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| No tracking (just save model files with a naming convention) | No structured way to compare runs, no registry stage concept, no reliable "current production model" pointer |
| Weights & Biases | Strong tracking UI, but the registry/deployment integration story is weaker for our self-hosted, Kubernetes-native stack than MLflow's |
| Custom registry (a table + S3 prefix convention) | Reinvents stage transitions, versioning, and artifact linking that MLflow already provides and the team would otherwise have to build and maintain |

## Consequences

- Adds a service to run and keep available: the MLflow tracking server. If it's
  down, Train Pipeline runs still execute but fail to log — this should alert
  (see `docs/observability.md`).
- Promotion to `Production` is a deliberate action (see `docs/model-lifecycle.md`)
  — nothing in this architecture auto-promotes a model based on metrics alone.
- Every model artifact remains recoverable from S3 even if the registry
  metadata is lost, since MLflow references artifacts by path rather than
  embedding them in PostgreSQL.