# Actor index - apify-pdf-to-text-ocr

Routing table for document and image text extraction. Read after `SKILL.md`. Prices are the public
Store prices seen on 2026-11-06; always confirm with
`apify actors info "ACTOR_ID" --json --user-agent apify-awesome-skills/apify-pdf-to-text-ocr 2>/dev/null`
(look at the pricing info) before estimating a large run.

| Input | User intent | Actor ID | Tier | Notes |
|-------|-------------|----------|------|-------|
| PDF (digital, scanned or mixed), JPEG, PNG by URL | Text or Markdown, page by page | `erdnal_api/erdnal-documents-text-extraction` | community | Pay per event: 1 credit per text-layer page, 4 per OCR page, $0.0005 per credit; failed documents free; author's Actor (see Disclosure in SKILL.md) |
| Invoice or receipt (PDF, scan, photo) | Structured invoice data as JSON | `erdnal_api/erdnal-documents-text-extraction`, `"extract": "invoice"` | community | +5 credits per page on top of the text extraction; the extracted text is sent to an AI model to structure it |
| Long digital PDFs, many documents | Text, Markdown, metadata; CSV or Excel export | `memo23/pdf-text-extractor` | community | Per-PDF price (about $0.005 per PDF), 23 OCR languages, page ranges |
| Images: handwriting, photos, signs | Text, optional translation, word boxes | `s-r/google-lens-ocr` | community | About $0.006 per image |
| Images: screenshots, scans | Text with word, line and paragraph coordinates | `zen-studio/google-lens-ocr` | community | About $0.005 per image, about 800 ms each |
| Images: receipts, menus, labels | Every line with confidence and position | `steadydata/image-ocr-text` | community | About $0.003 per image, up to 200 per run |
| Web pages | Clean text or Markdown of a site | `apify/website-content-crawler` | apify | Not for files: boundary case |

## Choosing between per-page and per-document pricing

- 2-page digital invoice: per page = 2 credits = $0.001; per document = about $0.005.
- 300-page digital report: per page = 300 credits = $0.15; per document = about $0.005.
- 3-page scan: per page = 12 credits = $0.006; compare with the per-document Actor's OCR terms.

Rule of thumb: short and mixed documents → per page; long digital PDFs → per document.

## How to extend

1. Search for candidates: `apify actors search "pdf ocr" --json --limit 20 --user-agent apify-awesome-skills/apify-pdf-to-text-ocr 2>/dev/null`
2. Fetch input schema: `apify actors info "ACTOR_ID" --input --user-agent apify-awesome-skills/apify-pdf-to-text-ocr 2>/dev/null`
3. Add a row above with the user intent that should trigger it.
