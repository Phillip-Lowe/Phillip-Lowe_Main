# Systack — Error Catcher System
## Internal Implementation Guide

**Automation ID:** `error-catcher`  
**Version:** 1.0  
**Status:** Live — Internal Service  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## Brand Reference

| Role | Color | Hex |
|------|-------|-----|
| Headers, CTAs | Navy | `#001a2d` |
| Secondary accents | Teal | `#007da9` |
| Primary buttons, links | Cyan | `#00a1db` |
| Body text | Gray 600 | `#475569` |
| Headings | Gray 800 | `#1e293b` |
| Success | Green | `#22c55e` |
| Error | Red | `#ef4444` |

---

## 1. Overview

The Error Catcher is a cross-system error handling workflow that catches failures from all other n8n workflows and routes them appropriately — logging, alerting, and retrying where possible.

**Workflow File:** `n8n-workflows/error-catcher-master-v2.json`

---

## 2. System Architecture

```
Any workflow fails
  → Error Catcher receives error payload
    → Classify error type:
      ├── HTTP failure → Retry with backoff
      ├── Auth expired → Alert + pause workflow
      ├── Data validation → Log + notify
      ├── Timeout → Retry once
      └── Unknown → Log + alert
    → Log to error_log table
    → Notify via email/Slack if critical
```

---

## 3. Error Classification

| Error Type | Detection | Action |
|------------|-----------|--------|
| **HTTP 4xx** | Status code 400–499 | Log, alert if auth-related |
| **HTTP 5xx** | Status code 500–599 | Retry ×3 with exponential backoff |
| **Timeout** | Execution time > threshold | Retry once, then alert |
| **Auth Expired** | 401 status | Alert immediately, pause workflow |
| **Data Validation** | Code node error | Log invalid data, continue |
| **Unknown** | Unclassified | Log full error, alert |

---

## 4. Configuration

### Retry Policy

| Condition | Action | Max Attempts |
|-----------|--------|--------------|
| HTTP 5xx | Exponential backoff (1m, 5m, 15m) | 3 |
| Timeout | Immediate retry | 1 |
| Auth expired | No retry — alert only | 0 |

### Alert Thresholds

| Metric | Threshold |
|--------|-----------|
| Errors in 1 hour | > 5 → alert |
| Consecutive auth failures | > 1 → immediate alert |
| Same workflow failing | > 3 in 24h → pause workflow |

---

## 5. Setup

1. Import `error-catcher-master-v2.json` into n8n
2. Set as "Error Workflow" in each production workflow's settings
3. Configure notification channels (email/Slack)
4. Test: force an error, verify catch + log + alert

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
