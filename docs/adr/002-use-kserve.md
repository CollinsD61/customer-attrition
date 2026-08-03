# ADR 002: Use KServe for Model Serving

## Status

Accepted

## Context

The churn model needs to be served as a low-latency prediction endpoint, with
support for versioned rollouts (so a new model can replace an old one without
downtime, and can be rolled back quickly). The serving layer must be decoupled
from the application backend so the model can be updated independently of
application code.

## Decision

Use **KServe** on Kubernetes as the model-serving layer. KServe is responsible
only for running inference; it is not the application backend. The FastAPI
Backend talks to KServe exclusively through
`backend/app/services/kserve_client.py`, never directly from route handlers.

The Deploy Pipeline publishes a new model version as a KServe
`InferenceService` custom resource; KServe handles revisioning and traffic
management.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| Serve the model inside the FastAPI process directly | Couples model lifecycle to application deploys; no independent scaling; harder rollback |
| Seldon Core | Comparable capability to KServe, but KServe has tighter integration with the model-registry-driven workflow we use and a simpler CRD surface for our needs |
| Plain Flask/FastAPI microservice per model, self-managed | Reinvents versioning, autoscaling, and health-checked rollout that KServe already provides |
| BentoML | Good option but adds a packaging step; KServe's direct consumption of registry artifacts fit our MLflow-centric flow better |

## Consequences

- Deploying a new model version is a Kubernetes-native operation (apply a CRD),
  fitting naturally into `k8s/` and existing manifest review practices.
- Adds an operational dependency on the KServe control plane running correctly
  in the cluster.
- Model input/output schema changes must be coordinated with
  `kserve_client.py` — a mismatch breaks the FastAPI ↔ KServe contract silently
  unless contract tests catch it (see `docs/model-lifecycle.md`).