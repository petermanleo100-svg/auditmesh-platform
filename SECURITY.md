# Security policy

Report vulnerabilities privately to the repository owner with affected commit, reproduction steps, impact and temporary mitigation. Never submit client evidence, access tokens, production events or account identifiers in a public issue.

Only the latest `main` baseline is supported. Production requires TLS, managed secrets, least-privileged database roles, private metrics and approved event-source identities. The pilot HS256 verifier must be replaced or governed through the enterprise identity platform before material audit reliance.

Release review covers authentication bypass, cross-tenant reads, forged events, duplicate/replay behavior, responsibility conflicts, unauthorized case closure, evidence mutation, denial of service and dependency advisories.
