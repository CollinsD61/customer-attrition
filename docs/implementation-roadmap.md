# Implementation Roadmap — Customer Churn MLOps Platform

## How to use this document

This file defines the **build order** for the project, matching the cluster as
it actually exists today — infrastructure is already provisioned in `kind`,
one namespace per service. This is different from a "build local first, add
Kubernetes later" flow: here, **infra comes first, business logic is written
against it from day one**.

An agent working through this file should complete phases in order, verify
each "Definition of done" before moving on, and never assume a service needs
to be stood up locally (in Docker) when it already exists in-cluster — connect
to it instead (via `kubectl port-forward` for local dev, or in-cluster DNS for
anything running inside the cluster).

Reference docs: `docs/architecture.md`, `docs/data-flow.md`,
`docs/feature-store.md`, `docs/model-lifecycle.md`, `docs/deployment.md`,
`docs/observability.md`, `docs/security.md`, `docs/testing-strategy.md`, and
`AGENTS.md` for exact dev commands.

## Current cluster state → component mapping

| Namespace | What runs here | Used starting in |
|---|---|---|
| `postgresql` | Shared Postgres (`airflow_db`, `mlflow_db`, `app_db`) | Phase 0 |
| `redis` | Feast online store | Phase 0 |
| `mlflow` | MLflow tracking server + registry | Phase 0 |
| `feast` | Feast registry only (no Feature Server — FastAPI embeds the Feast SDK directly and reads Redis itself) | Phase 0 |
| `airflow` | Airflow webserver + scheduler | Phase 0 |
| `cert-manager`, `knative-serving`, `kourier-system`, `kserve` | KServe control plane and its dependencies | Phase 0 |
| `ingress-nginx` | Cluster ingress | Phase 0 |
| `default` | Where the FastAPI backend and its `InferenceService` will be applied | Phase 5+ |

S3 is the one exception: it is **not** in the cluster. It's real AWS S3,
managed entirely via **AWS CLI**. Application code (pandas, Feast, MLflow)
still uses `boto3`/`s3fs` under the hood to read/write `s3://` paths — but all
bucket administration (create, upload, inspect) is done with the `aws` CLI.

---

## Phase 0 — Verify and connect to existing infrastructure

**Goal:** confirm every already-deployed service is healthy and reachable
before writing any code against it.

**Steps**

1. Confirm every namespace is healthy:
   ```bash
   kubectl get pods -n postgresql
   kubectl get pods -n redis
   kubectl get pods -n mlflow
   kubectl get pods -n feast
   kubectl get pods -n airflow
   kubectl get pods -n kserve
   ```
2. Set up local port-forwards for development (keep these running in separate
   terminals, or wrap them in a `Makefile`/script):
   ```bash
   kubectl port-forward -n postgresql svc/postgresql 5432:5432
   kubectl port-forward -n redis svc/redis 6379:6379
   kubectl port-forward -n mlflow svc/mlflow 5000:5000
   kubectl port-forward -n airflow svc/airflow-webserver 8080:8080
   ```
3. Confirm the three logical databases exist in the `postgresql` namespace's
   Postgres instance (`docs/adr/006-use-postgresql.md`):
   ```bash
   PGPASSWORD=<pw> psql -h localhost -U postgres -c "\l" | grep -E "airflow_db|mlflow_db|app_db"
   ```
   Create any that are missing.
4. Create the S3 bucket and folder layout via AWS CLI (external to the
   cluster):
   ```bash
   aws configure --profile churn-dev
   export AWS_PROFILE=churn-dev
   aws s3 mb s3://customer-churn-mlops-dev
   aws s3api put-object --bucket customer-churn-mlops-dev --key raw/
   aws s3api put-object --bucket customer-churn-mlops-dev --key processed/
   aws s3api put-object --bucket customer-churn-mlops-dev --key features/
   aws s3api put-object --bucket customer-churn-mlops-dev --key mlflow-artifacts/
   ```
5. Give the cluster access to S3: create a Kubernetes `Secret` (from a local,
   gitignored file — real values never committed) holding AWS credentials, in
   every namespace that needs S3 access (`airflow`, `mlflow`, `default` for the
   backend, and wherever Data/Train Pipeline jobs run). Use
   `k8s/secrets.example.yaml` as the template (`docs/security.md`).
6. Download/generate the churn dataset; commit only a trimmed sample to
   `data/samples/churn_sample.csv`; upload the full dataset via CLI:
   ```bash
   aws s3 cp ./local_data/churn_full.csv s3://customer-churn-mlops-dev/raw/churn_full.csv
   ```

**Definition of done**

All `kubectl get pods -n <ns>` checks above show `Running`/`Ready`, MLflow UI
loads at `localhost:5000`, Airflow UI loads at `localhost:8080`, and
`aws s3 ls s3://customer-churn-mlops-dev/raw/` shows the uploaded file.

---

## Phase 1 — Data Pipeline (run as a script against the real cluster, no DAG yet)

**Goal:** raw data becomes feature tables in S3, run by hand from a local
machine talking to the in-cluster/AWS services from Phase 0.

**Steps**

1. `mlops/src/customer_attrition/ingestion/` — read raw data from S3 (via
   `boto3`/`pandas.read_csv("s3://...")`, using the `churn-dev` AWS profile).
2. `mlops/src/customer_attrition/validation/` — schema/null/range checks; stop
   on failure.
3. `mlops/src/customer_attrition/preprocessing/` — clean/join, write to
   `processed/` in S3.
4. `mlops/src/customer_attrition/features/` — compute churn features, write to
   `features/` in S3.
5. `mlops/scripts/run_data_pipeline.py` — runner script chaining the four
   steps; this is what the Airflow DAG will call in Phase 7, unchanged.
6. Unit tests under `mlops/tests/unit/`, using the trimmed fixture — mock the
   S3 boundary, no real bucket access needed for unit tests.

**Definition of done**

```bash
python mlops/scripts/run_data_pipeline.py
aws s3 ls s3://customer-churn-mlops-dev/features/
pytest mlops/tests/unit
```
all succeed.

---

## Phase 2 — Feast

**Goal:** feature definitions exist and historical retrieval works, using the
already-deployed `feast` namespace.

**Steps**

1. **Decision (locked in):** the `feast` namespace runs registry-only — no
   Feature Server. FastAPI embeds the Feast Python SDK directly and reads
   Redis itself; nothing calls Feast over gRPC/HTTP. If nothing needs to run
   continuously in the `feast` namespace, a one-off `Job` (or none at all,
   with `feast apply` run from CI/a local machine) is enough — don't deploy a
   long-running Feature Server pod there.
2. Define entity (`customer_id`) and feature view(s) in `mlops/feast/`,
   pointing the offline source at
   `s3://customer-churn-mlops-dev/features/churn_features.parquet`.
3. Point the Feast registry at S3 (file-based registry, per
   `docs/feature-store.md`):
   ```bash
   aws s3api put-object --bucket customer-churn-mlops-dev --key feast-registry/
   ```
4. Apply definitions — either against the local repo (`feast apply`) or, if a
   Feast Operator manages the `feast` namespace, via whatever CR/CLI that
   operator expects. Confirm which applies by inspecting `kubectl get all -n
   feast` output from step 1.
5. Build a separate label table (churn ground truth); Feast does not generate
   labels.
6. Script `get_historical_features()` against the entity dataframe + labels;
   confirm the point-in-time join returns the expected columns.
7. Add tests under `mlops/feast/tests/`.

**Definition of done**

```bash
pytest mlops/feast/tests
```
passes, and historical retrieval produces the expected joined dataframe.

---

## Phase 3 — Train Pipeline + MLflow

**Goal:** train and register a model against the already-running MLflow server
in the `mlflow` namespace.

**Steps**

1. Point the MLflow client at the in-cluster server via the port-forward from
   Phase 0:
   ```bash
   export MLFLOW_TRACKING_URI=http://localhost:5000
   ```
2. `mlops/src/customer_attrition/training/` — train the classifier on the
   Phase 2 dataset.
3. Evaluate (AUC, F1, precision/recall) on a held-out split.
4. Log params/metrics/artifact to MLflow. Confirm artifacts land in
   `s3://customer-churn-mlops-dev/mlflow-artifacts/` (the MLflow server in the
   cluster needs the S3 secret from Phase 0 step 5 to write there).
5. `mlops/scripts/train_model.py` — runner script.
6. Register the run as a model version; set stage to `Staging`.

**Definition of done**

```bash
python mlops/scripts/train_model.py
```
completes; MLflow UI shows the run and registered version; artifact exists in
S3.

---

## Phase 4 — Materialize to the online store

**Goal:** the features used in training are available in the `redis`
namespace's Redis with millisecond lookup.

**Steps**

1. `mlops/scripts/materialize_features.py` — calls Feast's materialize
   operation. Point it at the Redis service (via port-forward locally, or
   in-cluster DNS `redis.redis.svc.cluster.local` when run from inside the
   cluster later).
2. Confirm a lookup by `customer_id` via the Feast Online SDK (or the Feature
   Server, if that's what Phase 2 step 1 found) returns the expected values.
3. Add a test that materializes a fixture and asserts the online read matches.

**Definition of done**

```bash
python mlops/scripts/materialize_features.py
```
completes; a lookup script returns features for a known `customer_id`.

---

## Phase 5 — KServe InferenceService

**Goal:** the registered model is callable as a live endpoint. Cluster-side
KServe dependencies (`cert-manager`, `knative-serving`, `kourier-system`,
`kserve`) are already installed — this phase is only about the model itself.

**Steps**

1. Write `serving/model_server/` only if the model needs custom pre/post
   processing; otherwise use KServe's built-in predictor for the model's
   framework.
2. Write `k8s/inference-service.yaml`, `storageUri` pointing at the model
   artifact in `s3://customer-churn-mlops-dev/mlflow-artifacts/...`,
   referencing the S3 secret from Phase 0.
3. Apply it (to `default`, or a dedicated `churn-serving` namespace if you
   prefer to keep it separate from the backend — decide and note the choice in
   `docs/deployment.md`):
   ```bash
   kubectl apply -f k8s/inference-service.yaml
   ```
4. Call the endpoint directly (`curl` or a test script) with a hand-built
   feature vector to confirm inference works, before wiring it to Redis.

**Definition of done**

```bash
kubectl get inferenceservice -n <namespace>
```
shows `Ready=True`; a manual request returns a prediction including model
version.

---

## Phase 6 — FastAPI Backend

**Goal:** one HTTP endpoint returns a churn prediction end-to-end, calling the
already-running Feast/Redis and KServe.

**Steps**

1. `backend/app/main.py` — FastAPI skeleton.
2. `backend/app/services/kserve_client.py` — the only module allowed to call
   KServe; points at the in-cluster `InferenceService` from Phase 5.
3. A feature-lookup service module — calls the Feast Online SDK directly
   against Redis (no Feature Server, per the Phase 2 decision). Not the route
   handler.
4. Prediction route handler: `customer_id` in → feature service → KServe
   client → prediction out. No direct `feast`/`redis` imports in the handler.
5. If `app_db` (in the `postgresql` namespace) is needed, set up
   `backend/app/db/migrations/`.
6. Tests under `backend/tests/unit` and `backend/tests/integration`.

**Definition of done**

```bash
uvicorn backend.app.main:app --reload
curl -X POST localhost:8000/predict -d '{"customer_id": "..."}'
pytest backend/tests/unit
```
all succeed, running locally but hitting the real in-cluster/AWS services via
port-forwards.

---

## Phase 7 — Airflow DAGs

**Goal:** Phases 1, 3, 4, and 5's deploy step run automatically via the
already-running Airflow in the `airflow` namespace, instead of by hand.

**Steps**

1. Get DAG files into the Airflow pods — check how DAGs are synced (git-sync
   sidecar, PVC, baked into the image) by inspecting the `airflow` namespace's
   deployment spec, and follow that mechanism rather than assuming one.
2. `dags/data_pipeline_dag.py` — thin DAG calling Phase 1's functions.
3. `dags/train_pipeline_dag.py` — thin DAG calling Phase 3's functions, ending
   in MLflow registration.
4. `dags/materialize_dag.py` — thin DAG calling Phase 4's materialize script,
   on its own schedule, independent of the other DAGs.
5. `dags/deploy_pipeline_dag.py` — thin DAG that loads the `Production`-staged
   model from MLflow and applies/updates `k8s/inference-service.yaml`
   (parameterizing `storageUri`) using the Kubernetes provider for Airflow —
   this requires the Airflow service account to have RBAC permission to modify
   `InferenceService` resources; add that permission as part of this phase.

**Definition of done**

```bash
kubectl exec -n airflow <scheduler-pod> -- airflow dags list-import-errors
```
returns empty; each DAG completes successfully when triggered manually from
the Airflow UI.

---

## Phase 8 — Codify infrastructure + CI/CD

**Goal:** the cluster state that currently exists only because someone ran
commands by hand is captured as reviewable, reproducible manifests — and CI
enforces quality gates.

This phase matters more than usual here, because the cluster was provisioned
before the manifests were necessarily written down. The check in "Definition
of done" is specifically designed to catch drift between what's running and
what's in Git.

**Steps**

1. For each namespace in the mapping table at the top of this document, write
   (or reverse-engineer via `kubectl get -o yaml`, then clean up) the
   corresponding manifests/Helm values into `k8s/`.
2. `k8s/secrets.example.yaml` — document every secret shape in use.
3. Enable/extend GitHub Actions:
   - `ci-python.yml` — lint/type-check/unit test backend + mlops + serving.
   - `ci-mlops.yml` (new) — `feast apply --dry-run`, DAG import-error check,
     `pytest mlops/tests/unit`.
   - `k8s-manifest-lint.yml` (new) — validate all YAML in `k8s/`.
   - `deploy-backend.yml`, `deploy-kserve.yml`, `deploy-airflow.yml` — apply
     manifests to the target cluster.

**Definition of done**

Tear down and recreate a **second** `kind` cluster using only what's in `k8s/`
(plus Phase 0's `aws s3 mb`/folder setup). If the same end-to-end prediction
check from Phase 6 passes on the new cluster, the manifests are trustworthy.
This is the single most important check in this roadmap — it's the only way
to know the documented infrastructure matches reality.

---

## Phase 9 — Observability + Security

**Goal:** FastAPI and KServe emit telemetry; secret/dependency scanning runs
in CI.

**Steps**

1. Instrument FastAPI and `kserve_client.py` with Datadog tracing; propagate a
   `trace_id` across the feature lookup and the KServe call.
2. Set up the three dashboards from `docs/observability.md`.
3. Add `security-scan.yml`: gitleaks/trufflehog, `pip-audit`, Trivy for
   container images.
4. Add a `model-contract-test.yml` gate before `deploy-kserve.yml` runs.

**Definition of done**

A deliberately malformed prediction request shows up as a traced event in
Datadog, and `security-scan.yml` fails the build when a fake secret is
committed on a test branch (verify once, then revert).

---

## Phase 10 — Frontend

**Goal:** a UI on top of the already-stable backend.

**Steps**

1. Build against the already-deployed, already-tested FastAPI endpoint from
   Phase 8 — not a mock.
2. Enable `ci-frontend.yml` and `deploy-frontend.yml`.

**Definition of done**

The frontend, running against the real in-cluster backend, displays a
prediction for a manually entered `customer_id`.

---

## Summary: what must never happen out of order

- No DAG (Phase 7) for a pipeline not already run and tested by hand
  (Phase 1, 3, 4).
- No new manifest assumed correct without the Phase 8 teardown-and-recreate
  check — infra existing today doesn't mean it's captured in Git yet.
- No `deploy-kserve.yml` running without a passing model contract test
  (Phase 9) gating it.
- No frontend work (Phase 10) against a backend that hasn't passed its own
  end-to-end check (Phase 6/8).