# Gotchas - apify-pdf-to-text-ocr

Cost guardrails, error recovery and pitfalls. Read on demand when building inputs or when a run fails.

## Cost guardrails

All Actors in this skill are pay per event or per result. Check the model with
`apify actors info "ACTOR_ID" --json --user-agent apify-awesome-skills/apify-pdf-to-text-ocr 2>/dev/null`
before a large run.

### Estimating `erdnal_api/erdnal-documents-text-extraction`

| What | Credits | Price ($0.0005 per credit) |
|------|---------|----------------------------|
| Page read from the PDF text layer | 1 | $0.0005 |
| Page read by OCR (scanned page, image) | 4 | $0.002 |
| Invoice data (`"extract": "invoice"`), per page | +5 | +$0.0025 |
| Run start | - | $0.00005 |

- Unknown mix of digital and scanned pages: estimate with the OCR price as the upper bound.
- Failed documents cost nothing; `includeMarkdown` and `includePages` cost nothing extra.
- The Actor respects the run's maximum cost (`maxTotalChargeUsd` in the API, "Max cost per run" in the
  Console): a document that would exceed the remaining budget is refused before OCR, not charged, and the
  run stops with a status message.
- Apify Store discounts apply on paid Apify plans (10 to 20 % off).

### Confirmation thresholds (suggested)

- Estimated cost **> $5** → warn the user.
- Estimated cost **> $20** → require explicit confirmation before running.
- Present cost as a rough estimate ("around $X"), not a guarantee.

## Common errors

| Error (`errorCode`) | Cause | Fix |
|---------------------|-------|-----|
| `document_url_unreachable` / `document_url_timeout` | Host down, 4xx/5xx, or slow | Retry later or ask for another link |
| `document_url_forbidden` | Not a public `https://` URL on port 443 (private IP, `http://`, custom port) | Ask for a public direct link |
| `document_url_redirect` | More than 3 redirects (share pages, login walls) | Use the direct download link |
| `unsupported_format` | Not PDF, JPEG or PNG | Convert first (HEIC, TIFF, WebP, DOCX are not read) |
| `pdf_encrypted` | Password-protected PDF | Ask for an unprotected copy |
| `too_many_pages` | More than 200 pages | Split with `pages` |
| `too_many_ocr_pages` | More than 5 OCR pages in one document | Split with `pages` (`1-5`, `6-10`, …) or route long scans to `memo23/pdf-text-extractor` |
| `max_credits_exceeded` | Document costs more than the remaining run budget | Raise the max cost per run or split the batch |
| `file_too_large` / `image_too_large` | Over 20 MB per file or 25 megapixels per image | Compress or split the file |

A run-level failure (`invalid_api_key`, `quota_exceeded`, `internal_error`) stops the run: report it to
the user rather than retrying in a loop.

## Actor-specific notes

### `erdnal_api/erdnal-documents-text-extraction`

- `mode: "auto"` is almost always right; `"ocr"` forces OCR on digital pages too (4 times the price).
- Set `languages` to the document's languages: OCR quality drops sharply with the wrong language.
- OCR takes about 3 to 4 s per page; a 5-page scan takes about 20 s.
- Tables come back as text in reading order, not as cells; handwriting is not read.
- Documents are processed in the EU and not kept after the response.

### Google Lens OCR Actors (`s-r/google-lens-ocr`, `zen-studio/google-lens-ocr`)

- Image URLs only; for a scanned PDF, extract or render pages to images first, or use a PDF Actor.
- Better on photos, handwriting and mixed scripts than Tesseract-based OCR; priced per image.
