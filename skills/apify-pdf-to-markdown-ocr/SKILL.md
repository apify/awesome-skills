---
name: apify-pdf-to-markdown-ocr
description: "Convert PDFs (born-digital or scanned) to clean Markdown or plain text with OCR in 19 languages, optional ruled-table extraction and RAG chunks with page numbers. Use when the user says: convert this PDF to markdown, extract text from a scanned PDF, OCR these PDFs, turn PDFs into chunks for RAG, get the text out of these invoices/letters/contracts."
author: Philipp Primisser
author_url: https://apify.com/prime619
metadata:
  category: data-extraction
  keywords: "pdf, ocr, pdf to markdown, pdf to text, scanned pdf, rag, chunking, tables, tesseract"
---

# PDF to Markdown / Text with OCR

Turns a list of PDF URLs into Markdown and plain text per file, using the PDF's text layer where it exists and OCR only on scanned pages.

Disclosure: the routed Actor `prime619/pdf-to-text-markdown-ocr` is built by the author of this skill and is a paid (pay-per-event) Actor. No affiliate parameters are used.

## Example prompts

Prompts this skill handles:

- "Convert these 3 PDF links to Markdown so I can load them into my RAG index."
- "This scanned German letter is a PDF on Google Drive — get me the text."

Out of scope (the boundary):

- "Fill in this PDF form / edit the PDF" — this skill only reads PDFs; use a PDF editing tool instead.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via `apify login` or the `APIFY_TOKEN` environment variable
- PDFs must be reachable by URL (direct links; Google Drive and Dropbox share links are accepted)

## Workflow

1. Collect the PDF URLs (max 500 per run). Ask whether the user wants Markdown (default) or plain text, and whether RAG chunks are needed.
2. Fetch the input schema to confirm field names.
3. Tell the user the price model before a large run: per PDF processed, per text page (first 15 pages per PDF) and per OCR page; set `maxPagesPerPdf` to cap long files.
4. Run the Actor and return the `markdown` / `text` fields (or the `markdownFile` / `textFile` links for long documents) plus `ocrConfidence` for scanned pages.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| PDF → Markdown/text, mixed digital + scanned, RAG chunks | `prime619/pdf-to-text-markdown-ocr` | community | OCR in 19 languages, tables, chunks with page numbers |

## Calling the Actor (Apify CLI)

    apify actors info "prime619/pdf-to-text-markdown-ocr" --input --json \
      --user-agent apify-awesome-skills/apify-pdf-to-markdown-ocr 2>/dev/null

    apify actors call "prime619/pdf-to-text-markdown-ocr" \
      -i '{"pdfUrls": [{"url": "https://www.irs.gov/pub/irs-pdf/fw9.pdf"}], "outputFormat": "markdown", "chunkForRag": true}' \
      --json \
      --user-agent apify-awesome-skills/apify-pdf-to-markdown-ocr \
      2>/dev/null

    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-pdf-to-markdown-ocr 2>/dev/null

Alternatively use the hosted Apify MCP server (<https://mcp.apify.com>).

## Troubleshooting

- Low `ocrConfidence` on phone photos → rerun with `"cleanScans": true`.
- Wrong OCR language guess → set `ocrLanguages` explicitly.
- Very long PDFs → set `pageRange` or `maxPagesPerPdf`; pages beyond the cap are skipped and not charged.
