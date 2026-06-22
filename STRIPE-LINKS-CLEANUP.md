# Stripe Payment Links Cleanup Guide

## ✅ KEEP These Active Links

| Name | Price | URL | Status | Action |
|------|-------|-----|--------|--------|
| SAOS Enterprise Fleet | $7,990/yr | `buy.stripe.com/...K0a` | Active | Set redirect: `https://systack.net/saos/onboard.html?session_id={CHECKOUT_SESSION_ID}&plan=enterprise` |
| SAOS Enterprise Fleet | $799/mo | `buy.stripe.com/...K0b` | Active | Set redirect: `https://systack.net/saos/onboard.html?session_id={CHECKOUT_SESSION_ID}&plan=enterprise` |
| SAOS Business Fleet — Annual | $2,988/yr | `buy.stripe.com/...K0c` | Active | Set redirect: `https://systack.net/saos/onboard.html?session_id={CHECKOUT_SESSION_ID}&plan=business` |
| SAOS Business Fleet — Monthly | $299/mo | `buy.stripe.com/...K0d` | Active | Set redirect: `https://systack.net/saos/onboard.html?session_id={CHECKOUT_SESSION_ID}&plan=business` |

## ❌ DEACTIVATE These (Duplicates/Wrong Pricing)

| Name | Price | URL | Status | Why Kill |
|------|-------|-----|--------|----------|
| SAOS Enterprise Fleet — Annual | $9,588/yr | OLD | Active | Wrong price — should be $7,990 |
| SAOS Business Fleet — Annual | $3,588/yr | OLD | Active | Wrong price — should be $2,988 |
| SAOS Enterprise Fleet — Monthly | $799/mo | OLD | Active | Dupe of Jun 19 link |
| SAOS Business Fleet — Monthly | $299/mo | OLD | Active | Dupe of Jun 19 link |
| SAOS Personal+ — Annual | $1,999/yr | OLD | Active | Product deprecated |
| SAOS Personal+ — Monthly | $199/mo | OLD | Active | Product deprecated |

## ❌ These Were Already Deactivated (Leave As-Is)

| Name | Price | Status |
|------|-------|--------|
| SAOS Enterprise Fleet — Monthly | $799/mo | Deactivated |
| SAOS Business Fleet — Monthly | $299/mo | Deactivated |
| SAOS Personal+ — Monthly | $199/mo | Deactivated |

## ⚠️ Systack Services (Different Onboarding — Don't Set SAOS Redirect)

| Name | Price | Type | Redirect |
|------|-------|------|----------|
| Systack Accelerate 10K — Monthly | $249/mo | Service | Manual/contact sales |
| Systack Private — Monthly | $799/mo | Service | Manual/contact sales |
| Systack Accelerate 25K — Monthly | $349/mo | Service | Manual/contact sales |
| Systack Accelerate Setup — One-time | $2,500 | Setup | Manual/contact sales |
| Systack Private Setup — One-time | $4,500 | Setup | Manual/contact sales |

---

## What Changed on Website

1. **pricing.html** — Removed Personal+ tier, fixed annual prices ($2,988/$7,990)
2. **saos/index.html** — Fixed annual prices ($2,988/$7,990)
3. **personal-agent/index.html** — Now redirects to /saos/
4. **All nav menus** — Removed "Personal Agent" link

## Next Steps

1. In Stripe dashboard, set redirects on the 4 KEEP links
2. Deactivate the 6 DUPLICATE/DEPRECATED links
3. Test with Stripe test mode: card `4242 4242 4242 4242`
4. Verify redirect lands on `systack.net/saos/onboard.html` with session info
