# Testing Strategy

This document describes the overall testing approach across the platform. It
complements the per-change checklists already in AGENTS.md ("Testing
requirements") by explaining *why* the test layers are split this way and how
they map to the architecture.

## Test layers

| Layer | Scope | Location | Runs against |
|---|---|---|---|
| Unit | A single function/module in isolation | `backend/tests/unit`, `mlops/tests/unit`, `serving/tests` | Mocked dependencies (no real S3, Redis, Feast, KServe) |
| Feast definition tests | Feature view/entity schema correctness | `mlops/feast/tests` | Local/test Feast repo, no live Redis/S3 required |
| Integration | Multiple components together | `backend/tests/integration` (create if not present) | Test doubles or local containers (e.g. local Postgres/Redis via `docker-compose`) |
| Contract | The boundary between FastAPI and KServe | `serving/tests` (prediction contract tests) | A test/staging KServe endpoint or a recorded contract fixture |

Run all Python tests with `pytest`; run only unit tests with the paths above
(see AGENTS.md → Development commands for exact commands).

## What to test, mapped to the architecture

### Data Pipeline changes

- Unit test each stage in isolation (ingestion, validation, preprocessing,
  feature engineering) with small, deterministic fixtures under
  `tests/fixtures/`.
- Validation logic specifically needs negative tests: malformed input should be
  rejected, not silently passed through.

### Feature engineering / Feast changes

- Add or update unit tests for the new/changed feature's output.
- Verify the output schema explicitly (column names, types).
- Verify entity key and event timestamp columns — this is the most common
  source of silent point-in-time join bugs.
- Run `pytest mlops/feast/tests` (Feast definition tests).

### Backend changes

- Add API or service-layer tests for any new/changed endpoint or service
  function.
- Preserve the `kserve_client.py` abstraction in tests — mock at that boundary,
  don't reach into KServe internals from a backend unit test.
- Assert route handlers never call Redis or Feast directly (this is a code
  review check as much as a test — a unit test can assert the route handler
  only depends on the service layer, not on `feast` or `redis` imports).

### Model serving changes

- Run prediction contract tests before promoting any model (see
  `docs/model-lifecycle.md`).
- Assert the input and output schema is unchanged, or that the change is
  intentional and versioned.
- Assert every prediction response includes the model version.

### Kubernetes / deployment changes

- Validate YAML (schema + syntax) as part of CI, not just locally.
- No test should require a real Secret value — use
  `k8s/secrets.example.yaml`-shaped fixtures.

## What is intentionally not covered by automated tests

- Exact model accuracy thresholds are an evaluation-time gate
  (`docs/model-lifecycle.md`), not a unit test — accuracy is data-dependent and
  doesn't belong in a pass/fail unit suite.
- Load/performance testing against KServe is out of scope for this document;
  track it separately if/when SLAs are formalized.

## CI expectations

Before merging, a PR should pass:

```bash
ruff check .
ruff format --check .
mypy backend mlops/src serving
pytest
```

(All commands from AGENTS.md → Development commands — this file does not
duplicate the exact commands, only explains what they're for.)