# Production runbook

## Go-live prerequisites

- Use encrypted managed PostgreSQL with point-in-time recovery and isolated migration credentials.
- Integrate the enterprise identity provider or rotate the pilot HS256 secret through a secret manager.
- Validate every policy against the control owner; activate policies through change control, not ad-hoc edits.
- Restrict event collectors to `collector`, reviewers to `auditor`, and protect metrics at the ingress.

## Startup and acceptance

1. Supply environment secrets and run `docker compose up -d --build`.
2. Gate traffic on `/health/ready` and monitor `/metrics`.
3. Test event idempotency, cross-tenant isolation, SLA calculation, optimistic concurrency and independent closure.
4. Reconcile source-system event counts to accepted events and rejected/dead-letter records before sign-off.

## Operational objectives

- Initial service target: 99.9% monthly after production baselining.
- Initial RPO/RTO: 15/60 minutes, subject to a customer restore drill.
- Alert on missing event sources, ingestion errors, critical overdue cases, readiness failures and database saturation.

During an incident, stop the affected collector, preserve raw evidence and database snapshots, revoke credentials, establish the last trusted event offset, replay idempotently into isolation, and require audit-owner approval before reopening case operations.

Portable backups use `auditmesh.backup`, AES-256-GCM and a secret-manager supplied 32-byte base64 key. Restore only into an empty database; the restore gate recomputes every retained canonical raw-event hash. Managed PostgreSQL PITR remains mandatory and both restore paths should be rehearsed quarterly.

Use `auditmesh-operations` for backup, restore and evidence verification; schedule `evidence-verify` and page on non-zero exit. The API rejects bodies over 2 MiB and bounds identity/control fields. Structured JSON access logs carry the response request ID for trace correlation.

The API database role must be `NOSUPERUSER NOBYPASSRLS` and must not own tables. A separate migration owner installs forced RLS. Each transaction sets `app.tenant_id`; direct SQL attack tests prove another tenant's rows remain invisible and unmodifiable.

The repository supports an enterprise pilot. A production audit conclusion additionally requires customer policy approval, evidence-retention decisions, source connector certification and independent control-owner acceptance.
