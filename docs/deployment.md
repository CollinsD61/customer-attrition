# Deployment

Covers how the platform is deployed to Kubernetes, and specifically how a model
goes from the MLflow Model Registry to a running KServe endpoint.

## Environments

For local/lab development this project runs on **`kind`** (Kubernetes-in-Docker),
a single-node local cluster. Manifests should stay environment-agnostic where
possible so the same YAML can later target a managed cluster (EKS/GKE/AKS)
without rewrites — only values like storage class or ingress class should differ
per environment.

## Directory layout

All Kubernetes manifests live in `k8s/`. Do not commit real Secret values — use
`k8s/secrets.example.yaml` as the template and generate real secrets locally or
via your cluster's secret manager.

## Components deployed to the cluster

| Component | Kind of resource |
|---|---|
| FastAPI Backend | Deployment + Service |
| KServe InferenceService | Custom resource (KServe CRD) |
| Redis | StatefulSet or managed service |
| PostgreSQL | StatefulSet or managed service (see `docs/adr/006-use-postgresql.md`) |
| Airflow | Deployment(s) (webserver, scheduler, workers) |
| MLflow tracking server | Deployment + Service |

## Deploy Pipeline mechanics

1. **Load model**: the pipeline reads the promoted version from the MLflow Model
   Registry.
2. **Deploy KServe**: it renders/applies a KServe `InferenceService` manifest
   pointing at that model's artifact location in S3, and applies it to the
   cluster.
3. KServe reconciles the resource and stands up (or updates) the serving pod(s).
4. The FastAPI backend's `kserve_client.py` is configured to call the
   InferenceService's internal endpoint — no manual wiring needed per deploy.

## Rolling out a new model version

Because KServe manages revisions, deploying a new version should be a
zero-downtime rollout:

1. Deploy Pipeline applies the updated `InferenceService` spec (new model URI).
2. KServe brings up the new revision, health-checks it, then shifts traffic.
3. If health checks fail, KServe keeps serving the previous revision — the
   pipeline should alert rather than silently leaving the cluster in a mixed
   state.

## Validating manifests before applying

- Validate YAML syntax and schema before `kubectl apply`.
- Never commit real Secret values.
- Any new infrastructure component (a new datastore, a new service) must not be
  introduced without: documenting the motivation, adding/updating an ADR,
  updating `docs/architecture.md`, updating this file, and adding relevant tests.

## Local development loop

```bash
# Bring up a local cluster
kind create cluster

# Apply manifests
kubectl apply -f k8s/

# Run the backend outside the cluster against local dependencies
uvicorn backend.app.main:app --reload
```