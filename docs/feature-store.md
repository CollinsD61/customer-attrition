# Feature Store (Feast)

Feast is the single source of truth for feature definitions and the only component
allowed to serve features — to training jobs (historical) and to the live API
(online). See `docs/adr/001-use-feast.md` for why Feast was chosen.

## Location in the repo

Feast definitions live in `mlops/feast/`. Feature computation logic does **not**
live here — Feast only defines and serves features; it does not compute them
(rule: Feast must not perform ETL). Computation happens in
`mlops/src/customer_attrition/features/` as part of the Data Pipeline.

## Offline vs online store

| | Offline store | Online store |
|---|---|---|
| Backend | S3 (`S3 Data Lake`) | Redis |
| Used by | Train Pipeline (historical retrieval) | FastAPI Backend (via Feast Online SDK) |
| Latency | Seconds (batch join) | Milliseconds |
| Freshness | As of last Data Pipeline run | As of last materialize run |
| Contains | Full feature history | Latest value per entity only |

## Feature retrieval (training)

Historical retrieval requires an **entity dataframe** with:
- `customer_id` (entity key)
- `event_timestamp`
- the churn label (sourced from a separate label table — Feast does not produce
  labels)

Feast performs a point-in-time join against the offline store so that a training
row only ever sees feature values that existed *before* its event timestamp,
preventing label leakage.

## Materialize job

```bash
python mlops/scripts/materialize_features.py
```

Copies the latest feature values from S3 into Redis. Run this on its own schedule,
separate from the Train Pipeline — training reads historical data and does not
depend on Redis being fresh.

## Registry

Feast needs a registry to store feature view/entity/data source definitions.

- **Default (recommended for this project):** file-based registry stored on S3
  alongside the offline store. Sufficient for a single-pipeline, low-concurrency
  setup.
- **Optional upgrade:** a SQL registry backed by `feast_db` in the shared
  PostgreSQL instance, if multiple people or pipelines need to write feature
  definitions concurrently. Not required for the current scale of this project.

## Change checklist

When adding or editing a feature definition:

1. Update the feature view in `mlops/feast/`.
2. Run `feast apply` (see AGENTS.md → Development commands).
3. Add or update a unit test for the new feature's output schema.
4. Verify the entity key and event timestamp columns are correct — this is the
   most common source of training/serving skew.
5. Run `pytest mlops/feast/tests`.
6. If the feature will be used online, confirm it survives a materialize run
   before relying on it in FastAPI.