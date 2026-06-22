# SAOS Enterprise Post-Payment Onboarding Form

## Deployed to: systack.net/saos/onboard.html

## Status: ✅ LIVE

### Features
- Visual region cards with flags
- Compliance badges per region
- Color picker with presets + custom hex
- Real-time location counter
- Progress bar (Account → Configuration → Deploy)
- Stripe session_id support
- Submits to n8n webhook: saos-enterprise-configure

### Stripe Checkout Redirect URL
```
https://systack.net/saos/onboard.html?session_id={CHECKOUT_SESSION_ID}
```

### Files
- `systack-site/saos/onboard.html` (deployed)
- `docs/post-payment-onboarding.html` (workspace backup)

### Related
- Webhook workflow: cAVqSVhMojNEa3hb
- Bridge: scripts/saos_provision_bridge.py
- Poller: scripts/n8n_execution_poller.py
