# Systack — SAOS Lead Capture + Stripe System
## Internal Implementation Guide

**Automation ID:** `saos-lead-capture`  
**Version:** 1.0  
**Status:** Live — Service Offered  
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

**SAOS (Service as a Service)** is Systack's food truck pitch system. It combines a lead capture landing page with Stripe payment links — prospects can view the offer and pay immediately. Built for pitching online ordering systems to food trucks.

**URL:** `https://systack.net/saos/`  
**Demo:** `https://systack.net/saos/demo.html`

---

## 2. System Architecture

```
Prospect visits SAOS landing page
  → Views pitch + pricing
    → Clicks "Get Started"
      → Fills lead form (name, email, truck name)
        → Form submits to n8n webhook
          → Lead logged to database
          → Stripe payment link generated
          → Prospect redirected to Stripe checkout
            → Payment completed
              → Confirmation page (thanks.html)
              → Internal notification
```

---

## 3. Core Components

### Frontend

| File | Purpose |
|------|---------|
| `saos/index.html` | Landing page with pitch + pricing |
| `saos/demo.html` | Interactive demo for prospects |
| `saos/thanks.html` | Post-payment confirmation |

### n8n Workflows

| Workflow | File | Purpose |
|----------|------|---------|
| Lead Capture | `saos/n8n-lead-workflow.json` | Receives form, logs lead |
| Payment Links | `saos/stripe-payment-links-workflow.json` | Generates Stripe checkout |

---

## 4. Setup Process (Replication)

### Step 1 — Deploy Landing Page

- Copy `saos/` directory to client domain
- Customize pitch copy for target industry
- Update pricing and features list

### Step 2 — Configure n8n

- Import lead capture workflow
- Import Stripe payment links workflow
- Set webhook paths
- Configure Stripe credentials

### Step 3 — Test

- Submit test lead → verify database logging
- Complete test payment → verify Stripe checkout
- Check confirmation page displays

---

## 5. Configuration

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `STRIPE_SECRET_KEY` | Stripe API authentication |
| `SAOS_WEBHOOK_PATH` | Lead capture endpoint |

---

## 6. Pitch Targets

See `saos/SAOS-PITCH-LIST.md` for compiled food truck targets in Little Rock metro.

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
