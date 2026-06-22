---
name: publish-verify
description: "Confirm deployed content is live and correct. Use after any publish, push, deploy, or content update."
---

# Publishing Verification

## Trigger
Any deployment or publish event: website update, GitHub Pages push, n8n workflow activation, email template deploy.

## Workflow

1. **Open published URL** — Production URL, not staging
2. **Confirm content exists** — Match against source of truth
3. **Check metadata** — Title tag, OG tags, favicon, preview image
4. **Validate links** — All internal links reachable
5. **Confirm load performance** — <3s to interactive

## Verification Gate
**FAIL IF:**
- [ ] URL returns 404 or redirect loop
- [ ] Content differs from intended (even slightly)
- [ ] Any link broken
- [ ] Page load >5 seconds without explanation

## Output
```
URL: <live URL>
Status: LIVE | BROKEN
Content Match: ✅ | ❌ <details>
Metadata: title=<val>, og:image=<val>
Links Checked: <N> total, <N> broken
Load Time: <N>s
Issues: <none or list>
```

## Escalation
SOL → ORACLE when:
- CDN caching prevents verification
- Rollback decision needed
- Multi-region deployment inconsistency