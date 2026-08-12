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
| Schema lifecycle | Alembic upgrade/downgrade round-trip test |
| Enterprise pilot | hardened PostgreSQL Compose, runbook and CI jobs |
| Database tenant defense | PostgreSQL FORCE RLS and transaction tenant context; direct SQL attack test |
| Verifiable evidence | canonical raw event retained; recomputation detects mutation |
| Backup and recovery | AES-256-GCM, exact Alembic-revision/empty-target gates and PostgreSQL clean-schema restore with evidence recomputation |
| Runtime abuse controls | 2 MiB body and bounded event/transition fields; oversize/invalid tests |
| Safe failure boundary | centralized SQLAlchemy 503; injected database failure leak test |
| Operability | structured request log, admin integrity API and operations CLI tests |
| Enterprise identity | OIDC/JWKS RS256/ES256, issuer/audience/expiry/role/tenant validation and 5-minute key cache; negative matrix |
| Auth downgrade control | production defaults OIDC; HMAC requires explicit exception; fail-closed settings tests |
| Actionable observability | versioned Prometheus 5xx, p95 latency and readiness alerts; `promtool` CI validation; routing is deployment-specific |
| Container supply-chain evidence | SPDX JSON SBOM for the built image; commit-pinned fixed-critical vulnerability gate and retained CI artifact |
