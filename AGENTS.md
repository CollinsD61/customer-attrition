# AGENTS.md

## Project overview

This repository implements an end-to-end customer attrition platform.

Main components:

- `frontend/`: user-facing web application
- `backend/`: FastAPI application API
- `mlops/`: data, feature, training, and deployment pipelines
- `mlops/feast/`: Feast feature repository
- `serving/`: custom model-serving code used by KServe
- `k8s/`: Kubernetes manifests
- `observability/`: Datadog dashboards and monitors
- `docs/`: architecture and operational documentation

## Architecture rules

1. Airflow orchestrates workflows but must not contain business logic. DAG files must stay thin; reusable logic belongs in service or domain modules.
2. Pipeline logic must live under `mlops/src/customer_attrition/`.
3. Feast manages feature definitions and retrieval. It must not perform ETL.
4. S3 stores raw data, processed data, feature tables, and MLflow artifacts.
5. Redis is used only as the Feast online store.
6. MLflow manages experiment metadata, model artifacts, and model registry.
7. KServe serves the model. It is not the application backend.
8. FastAPI is the application backend and communicates with KServe through
   `backend/app/services/kserve_client.py`.
9. Application logs, traces, and metrics must be instrumented for Datadog.
10. Secrets must never be committed to Git.

## Source layout

- Data ingestion:
  `mlops/src/customer_attrition/ingestion/`
- Data validation:
  `mlops/src/customer_attrition/validation/`
- Preprocessing:
  `mlops/src/customer_attrition/preprocessing/`
- Feature engineering:
  `mlops/src/customer_attrition/features/`
- Training:
  `mlops/src/customer_attrition/training/`
- Backend API:
  `backend/app/`
- Model server:
  `serving/model_server/`
- Feast definitions:
  `mlops/feast/`

## Documentation references

Before changing architecture, read:
- `docs/architecture.md`
- `docs/data-flow.md`

Before changing Feast definitions, read:
- `docs/feature-store.md`
- `docs/adr/001-use-feast.md`

Before changing training or model registration, read:
- `docs/model-lifecycle.md`

Before changing Kubernetes or deployment files, read:
- `docs/deployment.md`

Before changing logging, tracing, or monitoring, read:
- `docs/observability.md`

## Development commands

Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

Run Python linting:
```bash
ruff check .
```

Run Python formatting checks:
```bash
ruff format --check .
```

Run type checks:
```bash
mypy backend mlops/src serving
```

Run unit tests:
```bash
pytest backend/tests/unit mlops/tests/unit serving/tests
```

Run all Python tests:
```bash
pytest
```

Run the backend locally:
```bash
uvicorn backend.app.main:app --reload
```

Apply Feast definitions:
```bash
cd mlops/feast
feast apply
```

Run Feast definition tests:
```bash
pytest mlops/feast/tests
```

Materialize Feast features:
```bash
python mlops/scripts/materialize_features.py
```

Run the training pipeline locally:
```bash
python mlops/scripts/train_model.py
```

## Testing requirements

When changing feature engineering:
- update or add unit tests
- verify the output schema
- verify entity and event timestamp columns
- run Feast definition tests (`pytest mlops/feast/tests`)

When changing the backend:
- add API or service tests
- preserve the KServe client abstraction
- do not call Redis or Feast directly from API route handlers

When changing model serving:
- run prediction contract tests
- preserve the input and output schema
- include model version in responses

When changing Kubernetes manifests:
- validate YAML
- do not commit real Secret values
- use `k8s/secrets.example.yaml` for examples

## Data and artifact rules

Do not commit:
- raw datasets
- processed datasets
- Parquet feature tables
- model binaries
- MLflow local artifacts
- credentials
- `.env` files
- Kubernetes Secret values

Small samples may be committed only under:
- `data/samples/`
- `tests/fixtures/`

## Code conventions

- Use type hints for public Python functions.
- Keep API routes thin.
- Keep Airflow DAG files thin.
- Put reusable logic in service or domain modules.
- Do not use notebooks as production pipeline code.
- Avoid hard-coded bucket names, URLs, credentials, and environment names.
- Read configuration from environment variables or YAML configuration.
- Use structured logging.
- Propagate request and trace identifiers between backend and KServe.

## Change discipline

Do not introduce a new infrastructure component without:
- documenting the motivation
- adding or updating an ADR
- updating `docs/architecture.md`
- updating deployment documentation
- adding relevant tests

Do not modify generated files or dependency lock files unless the task requires it.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **customer-attrition** (340 symbols, 319 relationships, 0 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({search_query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.
- For security review, `explain({target: "fileOrSymbol"})` lists taint findings (source→sink flows; needs `analyze --pdg`).

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/customer-attrition/context` | Codebase overview, check index freshness |
| `gitnexus://repo/customer-attrition/clusters` | All functional areas |
| `gitnexus://repo/customer-attrition/processes` | All execution flows |
| `gitnexus://repo/customer-attrition/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
