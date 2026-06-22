# SAOS Plan Specifications (Updated June 2026)

## Business Fleet

| Specification | Value |
|---------------|-------|
| **Vultr Plan** | vhp-8c-16gb-amd |
| **vCPUs** | 8 |
| **RAM** | 16GB |
| **Storage** | SSD (plan-dependent) |
| **Region** | ord (Chicago) default |
| **OS** | Ubuntu 22.04 LTS |
| **Monthly Cost** | $96/mo |
| **Stripe Price** | $299/mo |

## Enterprise Fleet

| Specification | Value |
|---------------|-------|
| **Vultr Plan** | voc-g-8c-32gb-160s-amd |
| **vCPUs** | 8 |
| **RAM** | 32GB |
| **Storage** | SSD (optimized cloud) |
| **Region** | ord (Chicago) default |
| **OS** | Ubuntu 22.04 LTS |
| **Monthly Cost** | $240/mo |
| **Stripe Price** | $799/mo |

## Key Differences

| Feature | Business | Enterprise |
|---------|----------|------------|
| vCPUs | 8 | 8 |
| RAM | 16GB | 32GB |
| Plan Type | High Performance | Optimized Cloud |
| Multi-region | Optional | Up to 5 locations |
| Compliance | SOC2 | SOC2, HIPAA, GDPR |
| Support | Standard | Dedicated |

## Important Notes

- Both tiers use 8 CPU cores as of June 2026 update
- Enterprise includes double the RAM (32GB vs 16GB)
- Vultr Optimized Cloud (voc-g) provides better performance
- Account spending limits may affect provisioning
- Clean up old instances before provisioning new expensive ones

## Provisioning Pipeline

```
Customer pays via Stripe
        ↓
Webhook: saos-enterprise-configure
        ↓
Execution poller detects success
        ↓
DEPLOY task queued in Postgres
        ↓
Bridge provisions VPS via Vultr API
        ↓
VPS ready in ~8 minutes
```

## Regions Available

| Region | Location | Compliance |
|--------|----------|------------|
| ord | Chicago | SOC2 |
| lax | Los Angeles | SOC2, CCPA |
| lon | London | GDPR |
| ams | Amsterdam | GDPR |
| fra | Frankfurt | GDPR, BSI |
