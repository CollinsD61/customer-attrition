# ADR 001: Use Feast as the Feature Store

## Status

Accepted

## Context

The churn model needs features computed consistently for both training
(historical, batch) and serving (online, low-latency), without duplicating
feature logic in two places. Without a dedicated feature store, teams typically
end up with:

- Training-serving skew (the offline pipeline and the online API compute a
  feature slightly differently).
- No single definition of what a "feature" is, making features hard to reuse
  across models.
- No safe way to do point-in-time correct joins for training data, risking label
  leakage.

## Decision

Use **Feast** as the feature store. Feast owns feature *definitions* and feature
*serving* (both historical retrieval for training and online lookup for
inference). Feast does not perform ETL — feature computation stays in
`mlops/src/customer_attrition/features/`; Feast only defines the schema and
serves the already-computed values.

- **Offline store:** S3 (reuses the existing data lake, no new storage system).
- **Online store:** Redis (low-latency key-value lookup, industry-standard choice
  for Feast online serving).

## Alternatives considered

| Option | Why not chosen |
|---|---|
| No feature store (compute features ad hoc in both pipelines) | Highest risk of training/serving skew; features not reusable/discoverable |
| Tecton | Commercial, higher cost and operational complexity than needed at this scale |
| Hopsworks | Heavier to self-host; overlaps with capabilities we don't need yet (e.g. its own compute engine) |
| Build in-house (custom S3 + Redis sync scripts) | Reinvents point-in-time join logic, which is easy to get subtly wrong (label leakage) |

## Consequences

- Adds a new component (and a new step, `feast apply`) to the development
  workflow — see AGENTS.md.
- Requires a materialize job to keep Redis in sync with S3; if this job fails
  silently, online features go stale without an obvious error (mitigated by
  Datadog alerting — see `docs/observability.md`).
- Feature definitions become a shared, reviewable artifact (`mlops/feast/`)
  instead of scattered logic, which is a net positive for maintainability.