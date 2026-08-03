# Security

This document covers how secrets and sensitive configuration are handled across
the platform. The one rule that overrides everything else in this document:
**secrets must never be committed to Git.**

## What counts as a secret

- Database credentials (`airflow_db`, `mlflow_db`, `app_db`, `feast_db`)
- S3 access credentials
- Redis auth (if enabled)
- Datadog API/app keys
- Any FastAPI auth signing keys or session secrets
- TLS certificates/keys

## Where secrets live

| Environment | Mechanism |
|---|---|
| Local (`kind`) | Kubernetes `Secret` objects applied from a local, gitignored file, or environment variables loaded from a local `.env` (never committed) |
| CI | CI provider's secret store, injected as environment variables at run time |
| Production-like cluster | Kubernetes `Secret` objects, ideally sourced from an external secret manager (e.g. Vault, AWS Secrets Manager) rather than raw manifests |

`k8s/secrets.example.yaml` documents the **shape** of required secrets (key
names, expected format) with placeholder values only. Real secret manifests are
generated locally and never added to Git — add real secret file names to
`.gitignore` rather than relying on developers to remember not to `git add` them.

## Rules for code

- Never hard-code credentials, bucket names, or environment names in source —
  read them from environment variables or YAML configuration (see AGENTS.md →
  Code conventions).
- Do not log secret values, even at debug level. Structured logs sent to
  Datadog should have secret-shaped fields (tokens, passwords, keys) redacted
  before they're emitted.
- Database credentials are scoped per consumer (`airflow_db`, `mlflow_db`,
  `app_db`) — one component's credentials should not grant access to another's
  database. See `docs/adr/006-use-postgresql.md`.

## Data handling

- Customer data in S3 and PostgreSQL (`app_db`) should be treated as sensitive
  even though it is not itself a "secret" — access should be limited to the
  services that need it (Data Pipeline, FastAPI Backend), not broadly readable.
- Prediction request logs stored in `app_db` may contain customer identifiers —
  before sending equivalent data to Datadog for observability, hash or tokenize
  customer identifiers first (see `docs/observability.md`).

## Reviewing Kubernetes manifests

Before any manifest change is merged:

1. Validate YAML syntax and schema.
2. Confirm no real Secret values are present — only references to
   `k8s/secrets.example.yaml`-shaped objects.
3. Confirm no new hard-coded credentials were introduced in ConfigMaps (secrets
   belong in `Secret` objects, never `ConfigMap`).

## Incident response (secret leak)

If a secret is accidentally committed:

1. Rotate the credential immediately — assume it is compromised the moment it
   hits Git history, even if the commit is later removed.
2. Purge it from Git history (e.g. via `git filter-repo` or equivalent) as a
   follow-up — this is cleanup, not the fix; rotation is the fix.
3. Note the incident and the rotation in the relevant deployment doc or a
   post-mortem, so the exposure window is documented.