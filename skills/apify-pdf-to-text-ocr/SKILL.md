---
name: apify-pdf-to-text-ocr
description: Extract text from PDFs, scanned documents and images (image to text OCR) by URL with Apify Actors, page by page, as JSON, plain text or Markdown for LLM and RAG pipelines, and turn invoices and receipts into structured JSON. Routes each request to the right Actor - text-layer-first extraction for digital and mixed PDFs, Google Lens OCR for handwriting, translation and word boxes, per-document pricing for long PDFs - and estimates the cost before running. Use when the user asks to convert PDF to text, PDF to Markdown, OCR a scanned PDF, extract text from an image, screenshot or photo of a document, read a batch of PDF links, prepare documents for RAG or embeddings, parse an invoice or receipt to JSON, or says "pdf to text api", "ocr api", "image to text", "scanned pdf", "pdf parser", "extract text from this pdf". One routed Actor, erdnal_api/erdnal-documents-text-extraction, is built by this skill's author; every other row is unaffiliated (see Disclosure).
author: Erdnal (routes to a paid Actor built by the author; no affiliate or referral parameters)
metadata:
  category: data-extraction
  keywords: "pdf-to-text, ocr, image-to-text, pdf-to-markdown, scanned-pdf, pdf-extraction, text-extraction, pdf-parser, document-processing, invoice-to-json, receipt-ocr, rag, llm, tesseract, google-lens-ocr, handwriting-ocr"
---

# PDF to Text & OCR (PDFs, scans and images)

Turn documents into text an agent or a pipeline can use. Three questions decide which Actor fits, and
picking wrong is the main way this task wastes money:

- **Is the PDF digital, scanned, or mixed?** A digital PDF already contains its text: reading the text
  layer is exact, fast and cheap. Only scanned pages and images need OCR, which is slower and costs more.
  An Actor that OCRs every page pays the OCR price for text it could have read for free.
- **How long are the documents?** Per-page pricing is cheapest for short documents and mixed batches;
  per-document pricing wins for long digital PDFs (hundreds of pages).
- **What is in the image?** Printed text in a scan or screenshot is classic OCR. Handwriting, photos of
  signs, text that needs translation, or word-level coordinates are a job for Google Lens OCR Actors.

## Example prompts

Prompts this skill handles:

- "Extract the text from these 40 PDF links and give me one Markdown file per document for my RAG index."
- "This scanned contract is a PDF, OCR it in French and English and tell me which pages were hard to read."
- "Turn these supplier invoices into JSON with invoice number, date, VAT number, total and line items."

Out of scope (the boundary):

- "Convert this web page to Markdown" - not a document file: use `apify/website-content-crawler`.
- "Fill in this PDF form", "merge or compress these PDFs", "translate the PDF and keep the layout" - this
  skill extracts text, it does not edit or generate PDFs.

## Prerequisites

- Apify account ([sign up](https://apify.com)); the free plan's monthly credit covers small tests.
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)
- Documents reachable by a **public `https://` URL**. For local files, upload them first (for example to
  an Apify key-value store or any storage with a public or signed link).

## Workflow

1. **Classify the request** with the three questions above and pick the Actor from the routing table.
   Ask the user only if the answer changes the Actor (for example: "are these scans or digital PDFs?").
2. **Fetch the input schema** of the chosen Actor instead of guessing field names:

       apify actors info "erdnal_api/erdnal-documents-text-extraction" --input \
         --user-agent apify-awesome-skills/apify-pdf-to-text-ocr 2>/dev/null

   (`--input` prints the schema itself; adding `--json` would print the Actor's general info instead.)

3. **Estimate the cost** (see [references/gotchas.md](references/gotchas.md)) and tell the user. Ask for
   confirmation above about $5, which is roughly 10,000 text pages or 2,500 OCR pages with the default Actor.
4. **Run the Actor** and wait for it to finish:

       apify actors call "erdnal_api/erdnal-documents-text-extraction" \
         -i '{"documentUrls": ["https://api.erdnal.com/v1/documents/samples/demo-invoice.pdf"], "mode": "auto", "languages": ["eng"], "includeMarkdown": true, "includePages": false}' \
         --json \
         --user-agent apify-awesome-skills/apify-pdf-to-text-ocr \
         2>/dev/null

   The JSON output reports `run.status` (expect `SUCCEEDED`) and the dataset id at
   `storage.defaultDatasetId`. A 2-page document takes about 10 s; OCR adds 3 to 4 s per scanned page.
5. **Fetch and deliver** the results:

       apify datasets get-items "DATASET_ID" --format json \
         --user-agent apify-awesome-skills/apify-pdf-to-text-ocr 2>/dev/null > documents.json

   Report how many documents succeeded, how many pages went through OCR, the lowest OCR confidence, the
   credits charged, and every failed document with its `errorCode`. Save `markdown` or `text` to files if
   the user asked for files.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| PDF to text or Markdown, digital or mixed PDFs, scans, JPEG/PNG; batches of URLs | `erdnal_api/erdnal-documents-text-extraction` | community | Text layer first, OCR only for scanned pages; per-page price; 7 OCR languages; page-by-page output with confidence |
| Invoice or receipt to JSON | `erdnal_api/erdnal-documents-text-extraction` with `"extract": "invoice"` | community | Number, dates, supplier and VAT number, totals, tax lines, line items |
| Long digital PDFs (hundreds of pages), more OCR languages, metadata, CSV/Excel export | `memo23/pdf-text-extractor` | community | Per-document price; 23 OCR languages |
| Handwriting, photos, translation, word-level boxes | `s-r/google-lens-ocr` | community | Google Lens OCR with optional translation |
| Fast image OCR with word, line and paragraph coordinates | `zen-studio/google-lens-ocr` | community | About 800 ms per image, bounding boxes |
| Image OCR with every line, its confidence and position | `steadydata/image-ocr-text` | community | Screenshots, receipts, menus, labels |
| Web pages to text or Markdown (not files) | `apify/website-content-crawler` | apify | Boundary case: crawls sites, not documents |

Full table with input notes: [references/actor-index.md](references/actor-index.md).

## Input notes for the default Actor

`erdnal_api/erdnal-documents-text-extraction` (fetch the live schema in step 2; these are the fields
most requests need):

| Field | Values | Default | Notes |
|-------|--------|---------|-------|
| `documentUrls` | 1 to 500 public `https://` URLs | - | PDF, JPEG or PNG |
| `mode` | `auto`, `text`, `ocr` | `auto` | `auto` = text layer, OCR only where a page has no usable text |
| `languages` | 1 to 3 of `eng`, `fra`, `deu`, `spa`, `ita`, `por`, `nld` | `eng`, `fra` | OCR languages; set them to the document's languages |
| `pages` | e.g. `1-5,7` | all | Needed for long scans (5 OCR pages per document) |
| `includeMarkdown` | boolean | `false` | Adds `markdown`, one `## Page N` section per page, same price |
| `includePages` | boolean | `true` | Per-page `text`, `method`, `confidence`; turn off for smaller output |
| `extract` | `text`, `invoice` | `text` | `invoice` returns an `invoice` object instead of text |

Output, one item per document: `documentUrl`, `ok`, `inputType`, `pagesTotal`, `pagesProcessed`,
`ocrPages`, `text`, `markdown` (if requested), `chars`, `minConfidence`, `pages[]`
(`page`, `method`, `text`, `chars`, `confidence`), `invoice` (invoice mode), `creditsCharged`,
`errorCode`, `errorMessage`, `requestId`.

For RAG, split `markdown` on `## Page N` headings and keep the page number as chunk metadata, so answers
can cite the page.

## Calling Actors - other interfaces

- **Apify MCP connector** at <https://mcp.apify.com>: `call-actor` with the Actor id and the same input
  object, then `get-dataset-items`. To expose only this Actor:
  `https://mcp.apify.com?tools=erdnal_api/erdnal-documents-text-extraction`. Documented at
  <https://docs.apify.com/platform/integrations/mcp>.
- **MCP client of your choice** (e.g. [mcpc](https://github.com/apify/mcpc)).

## Troubleshooting

- `ok: false` with `document_url_unreachable`, `document_url_forbidden` or `document_url_redirect` → the
  link is not a public direct file link (login page, expired signed URL, more than 3 redirects): ask the
  user for a direct `https://` link. Failed documents are not charged.
- `too_many_ocr_pages` → the scan has more than 5 OCR pages: rerun with `pages` ranges (`1-5`, `6-10`, …)
  as separate URLs or runs, or route to `memo23/pdf-text-extractor`.
- `unsupported_format` → only PDF, JPEG and PNG: convert HEIC, TIFF or WebP images first.
- Low `minConfidence` (below about 0.8) → check `languages`, then try a Google Lens OCR Actor for
  photos and handwriting.
- More cost guardrails and error recovery: [references/gotchas.md](references/gotchas.md).

## Disclosure

`erdnal_api/erdnal-documents-text-extraction` is built and sold by this skill's author (Erdnal), with
pay-per-event pricing. Every other Actor in this skill is unaffiliated. No link carries an affiliate or
referral parameter. The routing table sends users to other Actors where they fit better.
