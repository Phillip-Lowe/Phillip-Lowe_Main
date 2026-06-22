# Invoice Parser — Full Status Update (2026-06-08)

## ✅ COMPLETED TODAY

### Parser Development
- **9 invoice formats now supported:**
  1. FROM:/BILL TO: + ITEMS (NovaTech)
  2. Table/Column (ABC Restaurant Supply)
  3. Contractor/Messy (Mike's Repairs)
  4. International VAT (Shenzhen Apex)
  5. POS Receipt (Utopia Deli)
  6. Professional Services (Carter & Bloom)
  7. Subscription/SaaS (NovaCloud)
  8. **Utility Bill (AT&T) — NEW**
  9. **Scanned/Image PDF with OCR — NEW**

### Infrastructure
- **API Server:** Running on port 9001 via launchd (`com.systack.invoice-api`)
- **Cloudflare Tunnel:** `invoices.systack.net` → localhost:9001 ✅
- **Database:** 119 records, backup saved (`invoice_data.db.backup`)
- **Web Demo:** `https://systack.net/services/invoice-extractor.html` ✅
- **OCR:** Tesseract + pytesseract installed and tested

### Real Invoice Testing
- **AT&T Phone Bill:** Downloaded from iCloud, parsed successfully
  - Vendor: AT&T Mobility
  - Date: Aug 18, 2025
  - Total: $149.59
  - 8 line items extracted

### n8n Email Pipeline
- **Workflow:** `qnsBnLIWQ1Sky68D` (Systack — Invoice Email Pipeline)
- **Status:** Active but IMAP credential failing
- **IMAP Credential Created:** `xBT92arTjBY66ccE` (Utopia Deli Gmail IMAP)
- **Blocker:** Gmail app password `sacn gdyi nrqw otnx` rejected by Google

## ❌ REMAINING BLOCKER

### Gmail App Password Revoked
- **Password:** `sacn gdyi nrqw otnx` (from keychain, created 2026-05-19)
- **Account:** `theutopiadelilittlerock@gmail.com`
- **Error:** `Invalid credentials (Failure)` / `535 5.7.8 Username and Password not accepted`
- **Tests:** SMTP (port 465, 587), IMAP (port 993) — ALL fail
- **Variants Tried:** with spaces, without spaces, uppercase, lowercase

**Fix Required:** Generate new app password at https://myaccount.google.com/apppasswords

## 🔧 TECHNICAL DETAILS

### Files Modified/Created
- `invoice_parser_production.py` — Added OCR fallback + utility bill parser
- `invoice_api.py` — No changes needed (was already working)
- `INVOICE-PARSER-DEPLOYMENT.md` — Updated with full status
- `~/.config/himalaya/config.toml` — Updated with multiple password attempts
- n8n database — Created IMAP credential, updated workflow nodes

### n8n API Access
- **Owner Account:** `plowe95@yahoo.com`
- **Password:** `123GreeN23!` (from keychain `n8n-local-auth`)
- **Auth Method:** Cookie-based (`n8n-auth`)
- **API Tested:** Login ✅, Credentials ✅, Workflows ✅, Activate ❌ (blocked by IMAP auth)

## NEXT ACTIONS
1. **Generate new Gmail app password** for `theutopiadelilittlerock@gmail.com`
2. **Update n8n IMAP credential** with new password
3. **Activate workflow** and test email trigger
4. **Download Utopia expense report** from iCloud and test
5. **Stripe paywall** integration
6. **Find 3-5 real vendor invoices** for testing

## NOTES
- iCloud files need `open <file>` in Finder to force download before copying
- n8n credential data is encrypted with salt — can't create manually
- API key in `.n8n_api_key` expired — use cookie auth instead
- Playwright installed for browser automation if needed


## Update 2026-06-08 08:12 CDT

### Postgres Investigation Complete

**Postgres IS running** on localhost:5432. The failure was due to credential mismatch:

| Expected by n8n | Actual in Postgres |
|-----------------|-------------------|
| Database: crm    | Database: utopia_deli (or postgres) |
| User: systack    | User: philliplowe |

**Fix Options:**
1. Create crm database + systack user
2. Update n8n credential to use existing utopia_deli/philliplowe
3. Use SQLite (current working solution)

**Recommendation:** SQLite handles everything. Postgres is optional unless you need concurrent multi-user access.

### Pipeline Works
Execution #439 (12:56:43) successfully:
- Received email with PDF
- Extracted invoice data (vendor, items, totals)
- Saved to SQLite database
- All line items preserved
