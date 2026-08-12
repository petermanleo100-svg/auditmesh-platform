# Production runbook

## Go-live prerequisites

- Use encrypted managed PostgreSQL with point-in-time recovery and isolated migration credentials.
- Integrate the enterprise identity provider or rotate the pilot HS256 secret through a secret manager.
- Validate every policy against the control owner; activate policies through change control, not ad-hoc edits.
- Restrict event collectors to `collector`, reviewers to `auditor`, and protect metrics at the ingress.

## Startup and acceptance

1. Supply environment secrets and distinct migration-owner/runtime credentials. For local Compose, use a fresh volume because runtime-role bootstrap runs only on initial database creation.
2. Run `auditmesh-operations preflight` as the runtime identity and require secret-free `valid: true` JSON.
3. Run `docker compose up -d --build`; Compose migrates as the owner and repeats preflight before the API starts.
4. Gate traffic on `/health/ready` and monitor `/metrics`.
5. Test event idempotency, cross-tenant isolation, SLA calculation, optimistic concurrency and independent closure.
6. Reconcile source-system event counts to accepted events and rejected/dead-letter records before sign-off.

## Operational objectives

- Initial service target: 99.9% monthly after production baselining.
- Initial RPO/RTO: 15/60 minutes, subject to a customer restore drill.
- Alert on missing event sources, ingestion errors, critical overdue cases, readiness failures and database saturation.

During an incident, stop the affected collector, preserve raw evidence and database snapshots, revoke credentials, establish the last trusted event offset, replay idempotently into isolation, and require audit-owner approval before reopening case operations.

Portable backups use `auditmesh.backup`, AES-256-GCM and a secret-manager supplied 32-byte base64 key. Restore only into an empty database already migrated to the exact application Alembic revision; restore never creates or upgrades schema implicitly. The gate recomputes every retained canonical raw-event hash. PostgreSQL CI migrates a clean schema and performs the encrypted restore. Managed PostgreSQL PITR remains mandatory and both restore paths should be rehearsed quarterly.

PostgreSQL event intake uses the `(tenant_id, event_id)` unique key with a database-native conflict path. Concurrent retries for the same event return the same case rather than surfacing a uniqueness failure; source connectors must preserve a stable event ID across retries.

Before approving a release, an administrator must run `GH_TOKEN=$(gh auth token) GITHUB_REPOSITORY=petermanleo100-svg/auditmesh-platform EXPECTED_REQUIRED_CHECKS=test,postgres,container,compose-smoke,analyze python scripts/verify_github_governance.py`. The verifier fails unless `main` protection, GitHub-Actions-bound checks, secret scanning/push protection and Dependabot security controls match the documented state. It intentionally runs outside Actions because the default workflow token cannot read administration settings; no broad administrator PAT is stored in Actions.

Use `auditmesh-operations` for backup, restore and evidence verification. Set `AUDITMESH_TEXTFILE_DIR` to a Node Exporter textfile-collector directory (or equivalent). Every command atomically writes a separate bounded-label metric and preserves last-success time after failure. Schedule `backup-create` and `evidence-verify`; page on non-zero exit, `operation_success == 0`, or backup age beyond the 15-minute RPO. An unwritable metrics directory is a deployment failure. The API rejects bodies over 2 MiB and bounds identity/control fields.

Load `deploy/prometheus/auditmesh-alerts.yml` into the approved Prometheus-compatible backend and map `owner=platform-operations` plus severity to named receivers. CI validates syntax and executes synthetic firing scenarios for readiness, 5xx rate, p95 latency, scheduled-operation failure and stale backup with `promtool`; receiver credentials and a real test notification remain environment acceptance evidence. CI runs `pip-audit`, retains an SPDX JSON image SBOM for 30 days, and blocks image vulnerabilities that are High/Critical with a known fix. Unfixed findings require explicit release risk review.

The `release-image` workflow has two modes. Manual dispatch creates a 14-day candidate image archive, checksum and SBOM, then records GitHub provenance and SBOM attestations without publishing a registry image. A `vX.Y.Z` tag publishes only that immutable commit to `ghcr.io/<owner>/auditmesh-platform`, records the registry digest, and attaches provenance plus SBOM attestations. Complete the release checklist before tagging; verify the published image with `gh attestation verify oci://ghcr.io/<owner>/auditmesh-platform:vX.Y.Z -R <owner>/auditmesh-platform`.

The API database role must be `NOSUPERUSER NOBYPASSRLS` and must not own tables. A separate migration owner installs forced RLS. Each transaction sets `app.tenant_id`; direct SQL attack tests prove another tenant's rows remain invisible and unmodifiable.

Production authentication defaults to `AUDITMESH_AUTH_MODE=oidc`; configure an HTTPS issuer/JWKS endpoint and exact audience. `kid`-selected signing keys cache for five minutes. HMAC is a controlled pilot exception requiring `AUDITMESH_ALLOW_HMAC_PRODUCTION=true`, a named risk owner and expiry date.

The repository supports an enterprise pilot. A production audit conclusion additionally requires customer policy approval, evidence-retention decisions, source connector certification and independent control-owner acceptance.
