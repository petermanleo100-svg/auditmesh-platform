# Enterprise pilot release checklist

- [ ] Main CI test, PostgreSQL and container jobs pass on the release commit.
- [ ] Control owners approve policy definitions, severity and SLA calendars.
- [ ] Every source connector has an authenticated identity, replay plan and count reconciliation.
- [ ] Security approves identity claims, secrets, TLS, ingress controls and database roles.
- [ ] Migration/rollback and backup/restore rehearsals pass in a production-like environment.
- [ ] Runtime database role is non-owner/NOBYPASSRLS and direct SQL RLS attacks are rejected.
- [ ] Cross-tenant attacks, duplicate events, concurrent transitions and self-closure are rejected.
- [ ] Critical overdue, readiness, ingestion error and source-gap alerts reach named owners.
- [ ] A synthetic case completes OPEN through independent CLOSED before real evidence is admitted.
- [ ] Oversize/invalid events and injected database failures pass negative tests without detail leakage.
- [ ] Scheduled `evidence-verify` and backup jobs use separate least-privileged operational identities.
- [ ] OIDC issuer/audience/roles/tenant mappings and signing-key rotation are tested; no unapproved HMAC exception remains.
