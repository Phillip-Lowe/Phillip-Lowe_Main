# Email Deliverability Guide

## Domain Warmup

When using a new domain or new sending setup:

1. **Week 1**: Send 5-10 emails/day to engaged recipients
2. **Week 2**: Increase to 15-20/day
3. **Week 3**: Increase to 25-30/day
4. **Week 4+**: Normal volume (up to your limits)

## SPF, DKIM, DMARC

### SPF Record
```
v=spf1 include:_spf.resend.com ~all
```

### DKIM
Automatically configured by Resend for verified domains.

### DMARC
```
v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com
```

## Inbox Placement Tips

- **Avoid spam words**: "free", "guaranteed", "no obligation"
- **Personalize subject lines**: Include company name or recipient name
- **Keep it short**: 2-3 paragraphs max
- **Clear unsubscribe**: Always include an easy way to opt out
- **Warm up the domain**: Gradually increase volume
- **Monitor reputation**: Use Resend dashboard to track bounces and complaints
