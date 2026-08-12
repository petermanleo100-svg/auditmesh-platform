# Capability–evidence matrix
| Capability | Evidence |
|---|---|
| Versioned policy-as-code | default policy installation and detection test |
| Idempotent event ingestion | repeated event returns existing case |
| Case governance | legal lifecycle, optimistic version and four-eyes closure tests |
| SLA operations | overdue case test |
| Deployability | API test, non-root image and CI |
| Auth and tenant binding | signed audit roles; scope/cross-tenant API test |
| Operations | request ID, metrics, probes and security headers test |
| Schema lifecycle | Alembic upgrade/downgrade round-trip test |
| Enterprise pilot | hardened PostgreSQL Compose, runbook and CI jobs |
| Database tenant defense | PostgreSQL FORCE RLS and transaction tenant context; direct SQL attack test |
| Verifiable evidence | canonical raw event retained; recomputation detects mutation |
| Backup and recovery | AES-256-GCM, empty-target restore and restored evidence verification tests |
