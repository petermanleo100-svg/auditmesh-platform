# Threat model

| Asset | Threat | Implemented control | Deployment responsibility |
|---|---|---|---|
| Control evidence | forged or altered event | signed collector identity, evidence hash, event idempotency | connector certificate/key and source reconciliation |
| Tenant cases | cross-tenant access | tenant from signed JWT and scoped queries | IdP claim governance and access review |
| Case closure | actor closes own violation | four-eyes closer rule and auditor scope | control-owner role mapping |
| Case history | concurrent/invalid transition | legal state machine, optimistic version and transition log | retention and immutable backup |
| SLA operations | missed critical case | severity deadlines and overdue queue | paging route, calendar policy and staffing |
| Availability | source gap or database outage | readiness/metrics/runbook | source heartbeat, HA database and restore drill |

Residual risk: production audit reliance requires source connector certification, policy-owner approval, immutable retention and database defense-in-depth beyond the application predicates.
