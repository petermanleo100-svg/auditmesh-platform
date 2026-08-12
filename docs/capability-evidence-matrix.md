# Capability–evidence matrix
| Capability | Evidence |
|---|---|
| Versioned policy-as-code | default policy installation and detection test |
| Atomic idempotent event ingestion | PostgreSQL `ON CONFLICT DO NOTHING` makes 24 concurrent deliveries return the same single case |
| Case governance | legal lifecycle, optimistic version and four-eyes closure tests |
| SLA operations | overdue case test |
| Deployability | API test, non-root image and CI |
| Auth and tenant binding | signed audit roles; scope/cross-tenant API test |
| Operations | request ID, metrics, probes and security headers test |
| Schema lifecycle | SQLite full-chain round trip plus PostgreSQL isolated-schema latest-revision downgrade/re-upgrade with business-row preservation and RLS-state verification |
| Enterprise pilot | hardened PostgreSQL Compose, runbook and CI jobs |
| Database tenant defense | PostgreSQL FORCE RLS and transaction tenant context; direct SQL attack test |
| Verifiable evidence | canonical raw event retained; recomputation detects mutation |
| Backup and recovery | AES-256-GCM, exact Alembic-revision/empty-target gates and PostgreSQL clean-schema restore with evidence recomputation |
| Runtime abuse controls | 2 MiB body and bounded event/transition fields; oversize/invalid tests |
| Safe failure boundary | centralized SQLAlchemy 503; injected database failure leak test |
| Operability | structured request log, admin integrity API and operations CLI tests |
| Enterprise identity | OIDC/JWKS RS256/ES256, issuer/audience/expiry/role/tenant validation and 5-minute key cache; negative matrix |
| Auth downgrade control | production defaults OIDC; HMAC requires explicit exception; fail-closed settings tests |
| Actionable observability | versioned API alerts plus atomic textfile metrics for scheduled backup/evidence operations, preserving last-success time on failure; unit/CLI tests and synthetic `promtool` firing drills cover API, operation failure and stale backup; collector mounting, receiver credentials and delivery are deployment-specific |
| Container supply-chain evidence | SPDX JSON SBOM, Python dependency audit and fixable High/Critical image vulnerability gate; commit-pinned actions, retained CI artifact and an expiring, source-checked exception for CPython `CVE-2026-15308` because the affected HTML parser is outside the service path |
| Verifiable image release path | manual candidate archive with checksum/SBOM/attestations; SemVer tags publish digest-addressed GHCR images with provenance and SBOM attestations; formal publication remains tag-controlled |
| Environment admission preflight | fail-closed production config, runtime role privilege/ownership checks, exact Alembic revision, forced RLS and 32-byte backup-key validation; PostgreSQL positive/owner-negative integration test and full Compose readiness smoke job |
| Release-bound environment evidence | fail-closed admission manifest binds source reconciliation, control approval, IdP, PITR, rollback and alert-delivery evidence to the exact release SHA; positive and negative tests plus non-zero CLI contract |
| Repository security governance | protected `main`, strict required CI/CodeQL checks, enforced administrators, linear history, resolved discussions, no force-push/delete, secret scanning/push protection and Dependabot security updates; live GitHub protection/security API audit, rechecked at release |
