# PDF Generation Skill — Utopia Deli Docs

## Purpose
Generate branded PDFs from Markdown source files for Utopia Deli documentation.

## Requirements
- pandoc 3.10+
- Basic LaTeX or wkhtmltopdf (fallback)

## Usage

### Generate PDF from Markdown
```bash
cd /Users/philliplowe/utopia-deli-order/docs/automations/{category}/{client|internal}
pandoc {source}.md -o {output}.pdf \
  --metadata title="{Title}" \
  --metadata author="The Utopia Deli" \
  --metadata date="$(date +%Y-%m-%d)" \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -V colorlinks=true
```

### Archive Legacy PDF
```bash
mkdir -p archive
mv {old-version}.pdf archive/{old-version}-v{OLD_VER}.pdf
```

### Batch Update Category
```bash
for f in *.md; do
  base=$(basename "$f" .md)
  if [ -f "$base.pdf" ]; then
    mkdir -p archive
    mv "$base.pdf" "archive/$base-$(date +%Y%m%d)-legacy.pdf"
  fi
  pandoc "$f" -o "$base.pdf" --metadata title="$base"
done
```

## Affected Docs from 2026-06-20 Session
| Category | File | Change |
|----------|------|--------|
| order-system | client service manual | Consent text, field order, pickup removed, juice price |
| order-system | implementation guide | Consent text, field order, pickup removed, juice price |
| order-system | troubleshooting guide | Footer links fix |
| meal-prep | client service manual | "Pick your" → "Get your", field order, consent, pickup |
| meal-prep | implementation guide | Address links, field order, consent |
| noshow-prevention | all docs | Add to archive (superseded by messaging system) |

## Brand Template
- Font: Open Sans
- Primary color: #590B3F
- Accent: #AF3D4B
- Secondary: #754681

## Version Convention
- v1.0 = Initial release
- v1.1 = Minor updates (content changes)
- v2.0 = Major restructuring
- Date suffix for interim builds: -2026-06-20
