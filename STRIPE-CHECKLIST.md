# Stripe Redirect Setup — Checklist

## Step 1: Set Redirect URLs (4 links)

Go to https://dashboard.stripe.com/payment-links

For each ACTIVE link below:
1. Click "Edit" on the link
2. Scroll to "After payment"
3. Select "Redirect customers to your website"
4. Paste the URL
5. Save

### Business Monthly ($299)
- **URL:** `https://systack.net/saos/onboard.html?session_id={CHECKOUT_SESSION_ID}&plan=business`
- **Status:** ❌ Not set yet

### Business Annual ($2,988)
- **URL:** `https://systack.net/saos/onboard.html?session_id={CHECKOUT_SESSION_ID}&plan=business`
- **Status:** ❌ Not set yet

### Enterprise Monthly ($799)
- **URL:** `https://systack.net/saos/onboard.html?session_id={CHECKOUT_SESSION_ID}&plan=enterprise`
- **Status:** ❌ Not set yet

### Enterprise Annual ($7,990)
- **URL:** `https://systack.net/saos/onboard.html?session_id={CHECKOUT_SESSION_ID}&plan=enterprise`
- **Status:** ❌ Not set yet

---

## Step 2: Deactivate Old Links (6 links)

In Stripe dashboard, find these and click "Deactivate":

| Name | Price | Why |
|------|-------|-----|
| SAOS Enterprise Fleet — Annual | $9,588/yr | Wrong price |
| SAOS Business Fleet — Annual | $3,588/yr | Wrong price |
| SAOS Enterprise Fleet — Monthly | $799/mo | Duplicate (old) |
| SAOS Business Fleet — Monthly | $299/mo | Duplicate (old) |
| SAOS Personal+ — Annual | $1,999/yr | Deprecated |
| SAOS Personal+ — Monthly | $199/mo | Deprecated |

---

## Step 3: Test

Use Stripe test mode: Card `4242 4242 4242 4242`, any future date, any CVC

Expected flow:
1. Click Business Monthly button on systack.net/saos
2. Complete test payment
3. Redirect to systack.net/saos/onboard.html?session_id=xxx&plan=business
4. Form shows "SAOS Business Fleet"
5. Submit form → webhook → provisioning pipeline starts

---

## Current Status

| Component | Status |
|-----------|--------|
| Website pricing | ✅ Updated |
| Onboard form | ✅ Reads plan param |
| Webhook bridge | ✅ Running on port 8767 |
| Vultr API | ✅ Tested, working |
| Stripe redirects | ❌ Not configured yet |
| Pipeline end-to-end | ❌ Not tested yet |
