# Observability

All application logs, traces, and metrics must be instrumented for Datadog
(architecture rule). This document says what is instrumented, where, and why.

## What gets observed

| Component | Why | Signal types |
|---|---|---|
| **FastAPI Backend** | Every prediction request passes through it; the primary place to see latency and error rate as experienced by clients | Logs, traces, metrics |
| **KServe** | Model inference latency and errors directly affect prediction quality and SLAs | Logs, traces, metrics |
| **Airflow** | Pipeline failures need to be caught before they cause stale data or a bad model to reach production | Task logs, run metrics |

FastAPI and KServe sit on the **runtime** path (see `docs/data-flow.md` §4) and
are the highest-priority targets — a failure there affects live users
immediately. Airflow failures are batch and typically have more slack to detect
and fix, but are still monitored via the same principle (its own task
logs/metrics feed Datadog through the Datadog Airflow provider).

## Request tracing

Request and trace identifiers must be propagated from FastAPI through to KServe
(rule in AGENTS.md → Code conventions). This means a single `trace_id` should let
you follow one prediction request across:

```
Client → FastAPI → Feast Online SDK / Redis → FastAPI → KServe → FastAPI → Client
```

Without this, a slow or failed prediction can't be diagnosed — you'd only see
"FastAPI was slow" without knowing whether the bottleneck was the feature lookup
or the model call.

## What to alert on (starting set)

- FastAPI 5xx rate above baseline
- FastAPI/KServe p95 latency above SLA
- KServe inference errors (model exceptions, schema mismatches)
- Redis lookup failures or timeouts (usually indicates a stale/missing
  materialize run)
- Airflow task failures in any of the three pipelines
- Feature drift, once instrumented (compares live feature distributions to the
  training-time distribution)

## Dashboards

Suggested minimum set of Datadog dashboards:

1. **Serving health** — FastAPI + KServe latency, error rate, throughput.
2. **Pipeline health** — Airflow DAG success/failure over time, per pipeline.
3. **Model performance** — prediction volume by model version, drift indicators
   once available.

## Adding new instrumentation

When changing logging, tracing, or monitoring:

1. Read this document and confirm the change fits one of the categories above.
2. Use structured logging (no unstructured string concatenation) so Datadog can
   parse fields.
3. Make sure any new metric/trace doesn't leak PII (customer identifiers should
   be hashed or tokenized before being sent to Datadog).