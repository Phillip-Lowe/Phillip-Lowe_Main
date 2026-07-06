# SAOS Risk Register

**PESSI ⚠️ | Risk Assessment**
**Version:** 1.0 | **Date:** 2026-07-06

---

## Risk Register

| # | Risk | Category | Probability | Impact | Risk Score | Mitigation | Owner | Review Date |
|---|------|----------|-------------|--------|------------|------------|-------|-------------|
| 1 | **Server hardware failure** — MacBook Air SSD/RAM failure takes all services offline | Technical | Low | Critical | **High** | Cloud backup of critical configs; migration plan to VPS/cloud hosting | SOL | 2026-07-20 |
| 2 | **Database corruption** — PostgreSQL data loss due to power outage or bug | Technical | Low | Critical | **High** | Daily automated backups + verification; pg_dump + restore tested; 30-day retention | SOL | 2026-07-20 |
| 3 | **Rate limit exhaustion** — Login rate limiter blocks legitimate users during high traffic | Technical | Medium | High | **Medium** | Rate limits tuned per endpoint; monitoring alerts on rate limit hits; adjustable thresholds | PESSI | 2026-07-20 |
| 4 | **Client data leak** — Multi-tenant isolation failure exposes one client's data to another | Security | Low | Critical | **High** | All queries scoped by client_id; audit logging on all access; regular penetration testing planned | PESSI | 2026-07-20 |
| 5 | **Credential exposure** — API keys or DB password leaked in logs or git | Security | Medium | High | **Medium** | .gitignore excludes secrets; env vars for credentials; API key rotation policy; never log tokens | PESSI | 2026-07-20 |
| 6 | **Stripe payment failure** — Subscription payment fails, customer churns | Financial | Medium | Medium | **Medium** | Automated retry on failed payments; dunning emails via CHATTY; manual outreach for high-value accounts | Green | 2026-07-20 |
| 7 | **Customer churn due to poor onboarding** — Client can't get set up, abandons | Business | Medium | High | **Medium** | Automated onboarding script; welcome guide + videos; dedicated onboarding call for Enterprise; 30-day check-in | SOL | 2026-07-20 |
| 8 | **Competitive displacement** — Cheaper/better alternative enters market | Business | Medium | Medium | **Medium** | ATLAS competitive monitoring; continuous feature improvement; customer lock-in via integrations | ATLAS | 2026-07-20 |
| 9 | **Legal liability from automation errors** — SAOS automation causes client financial loss | Legal | Low | Critical | **High** | JURIS MSA with limitation of liability clause; insurance review; "beta" disclaimers where appropriate | JURIS | 2026-07-20 |
| 10 | **Non-compliance with data regulations** — GDPR, CCPA, HIPAA exposure | Legal | Low | Critical | **High** | Compliance policies in place; data retention policy; trust center public docs; DPA available | JURIS | 2026-07-20 |
| 11 | **Key person dependency** — Green/SOL are single points of failure | Operational | High | High | **High** | Documentation (this playbook); runbooks for each system; ASSEMBLY deployment kit; eventual team expansion | Green | 2026-07-20 |
| 12 | **Cloudflare Tunnel failure** — SSL/cert issue blocks all mobile access | Technical | Low | Critical | **High** | Backup .ts.net URLs still active; monitoring on tunnel health; manual DNS fallback documented | SOL | 2026-07-20 |
| 13 | **n8n workflow breakage** — Critical automation stops working silently | Technical | Medium | High | **Medium** | Fleet health monitor checks n8n every 15 min; webhook monitoring; version pinning for workflows | PESSI | 2026-07-20 |
| 14 | **Bad customer data poisons system** — Client uploads malformed data that breaks automation | Technical | Medium | Medium | **Medium** | Input validation on all endpoints; sandbox testing for new integrations; rollback capability | CODY | 2026-07-20 |
| 15 | **Cash flow crisis** — Not enough customers to cover infrastructure costs | Financial | Medium | Critical | **High** | Monthly cost tracking ($0 infra currently); target MRR $1,000 before scaling; bootstrap-first approach | Green | 2026-07-20 |

---

## Risk Heat Map

```
Impact →    Low    Medium    High    Critical
Probability
    High    —       11        —       15
    Medium  —       6, 8      3, 7    5, 13, 14
    Low     —       —         2       1, 4, 9, 10, 12
```

---

## Security Review

### 1. Authentication

| Area | Current State | Gaps Found | Recommendations | Priority |
|------|---------------|------------|-----------------|----------|
| PIN-based login | ✅ Working, rate-limited (5/5 min) | No brute force protection beyond rate limit | Add progressive delay after failed attempts | Medium |
| MFA (TOTP) | ✅ Implemented, RFC 6238 compliant | Adoption rate unknown (0 of 2 clients) | Make MFA mandatory for Enterprise tier | Medium |
| Session tokens | ✅ 30-day expiry, SHA-256 hashed | No refresh token mechanism | Implement token refresh for long sessions | Low |
| Token revocation | ✅ On PIN change, logout | No global token revocation for admin | Add "Revoke all sessions" endpoint | Low |

**Score:** 🟢 Strong

### 2. Client Isolation

| Area | Current State | Gaps Found | Recommendations | Priority |
|------|---------------|------------|-----------------|----------|
| Data scoping | ✅ All queries filter by client_id | Row-level security not enforced at DB level | Add PostgreSQL RLS policies | Medium |
| Cross-client access | ✅ Blocked by auth decorators | No automated test for isolation breach | Add integration test for multi-tenant isolation | Medium |
| Admin access | ✅ Admin endpoints require admin role | No admin action logging beyond audit_log | Add real-time admin activity alerts | Low |

**Score:** 🟢 Strong

### 3. API Security

| Area | Current State | Gaps Found | Recommendations | Priority |
|------|---------------|------------|-----------------|----------|
| Rate limiting | ✅ 8 per-endpoint configs with headers | No distributed rate limiting (memory only) | Add Redis-backed rate limiting for multi-instance | Low |
| RBAC | ✅ 5 roles with decorators | Role hierarchy not implemented | Add role inheritance (admin > ops > support > billing > customer) | Low |
| Input validation | ✅ Basic validation on all endpoints | No SQL injection test suite | Add parameterized query audit + SQLi tests | Medium |
| CORS | ✅ Restricted to authorized domains | Hardcoded localhost in dev | Make CORS origins configurable per environment | Low |

**Score:** 🟢 Strong

### 4. Credential Storage

| Area | Current State | Gaps Found | Recommendations | Priority |
|------|---------------|------------|-----------------|----------|
| DB password | ✅ In env var, not in code | Stored in launchd plist (readable by system) | Move to keychain or secrets manager | Medium |
| API keys | ✅ Internal API key in env var | Dev key still in use (`saos-internal-dev-key`) | Rotate to 64-char hex production key | High |
| Stripe keys | ✅ Live restricted key | Key has broad permissions | Restrict Stripe key to minimum required permissions | Medium |
| Session tokens | ✅ SHA-256 hashed in DB | Plain tokens in memory during session | Acceptable for current scale | Low |

**Score:** 🟡 Adequate (needs API key rotation)

### 5. Backups

| Area | Current State | Gaps Found | Recommendations | Priority |
|------|---------------|------------|-----------------|----------|
| Frequency | ✅ Daily at 3 AM CDT | No hourly/incremental backup | Add hourly WAL archiving for point-in-time recovery | Low |
| Verification | ✅ Automated verify + restore test | Only tests local restore, not cross-machine | Add remote restore test quarterly | Medium |
| Retention | ✅ 30 days local | No off-site backup | Upload to S3 or Backblaze B2 | Medium |
| Encryption | ❌ Not encrypted at rest | Backup files are plain SQL | Encrypt backups with GPG or age | Medium |

**Score:** 🟢 Strong (local), 🟡 Adequate (off-site)

### 6. Disaster Recovery

| Area | Current State | Gaps Found | Recommendations | Priority |
|------|---------------|------------|-----------------|----------|
| RPO | ✅ 24 hours (verified) | Point-in-time recovery not possible | Add WAL archiving for PITR | Low |
| RTO | ✅ 6 minutes (verified) | Restore procedure not documented step-by-step | Create runbook with exact commands | Medium |
| DR site | ❌ None | Single point of failure (one MacBook) | Plan migration to cloud VPS for HA | Low |
| Test frequency | ✅ Monthly verification | No annual full DR drill | Schedule quarterly DR drill | Low |

**Score:** 🟡 Adequate (single site)

---

## Top 5 Critical Fixes Before Scale

| # | Fix | Why | Timeline |
|---|-----|-----|----------|
| 1 | **Rotate `SAOS_INTERNAL_API_KEY`** | Dev key is predictable and may be in logs | This week |
| 2 | **Add PostgreSQL RLS policies** | Row-level security prevents multi-tenant data leak | This month |
| 3 | **Encrypt backups** | Unencrypted backups are a liability if machine is stolen | This month |
| 4 | **Add off-site backup storage** | Single-machine backup is not DR-ready | This month |
| 5 | **MFA mandatory for Enterprise** | Enterprise clients expect MFA; currently optional | Before first Enterprise client |

---

## Security Scorecard

| Domain | Score | Status |
|--------|-------|--------|
| Authentication | 8.5/10 | 🟢 |
| Client Isolation | 7/10 | 🟢 |
| API Security | 7.5/10 | 🟢 |
| Credential Storage | 6/10 | 🟡 |
| Backups | 7/10 | 🟢 |
| Disaster Recovery | 5/10 | 🟡 |
| **Overall** | **6.8/10** | **🟡** |

---

## Review Schedule

- **Weekly:** PESSI reviews security events, failed logins, rate limit hits
- **Monthly:** Full risk register review and update
- **Quarterly:** Security review + penetration test plan
- **Annually:** Full DR drill + compliance audit

---

*This is a living document. Update after every incident, quarterly minimum.*
