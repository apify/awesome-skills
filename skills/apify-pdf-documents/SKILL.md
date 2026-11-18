---
name: apify-pdf-documents
description: >-
  Extract data from PDFs and images with pay-per-use Apify Actors: tables to rows (bank statements, invoices, reports, ready for CSV or Excel), text page by page for RAG and search, and OCR for scanned PDFs and images in 100+ languages. Use when the user says "pdf to excel", "extract tables from this pdf", "convert bank statement to csv", "pdf to text", "ocr this scan", "read text from image", or "chunk this pdf for rag".
author: Rowfeed
author_url: https://apify.com/rowfeed
metadata:
  category: data-extraction
  keywords: "pdf, pdf to excel, pdf to csv, pdf table extraction, bank statement converter, pdf to text, ocr, scanned pdf, image to text, rag, document parsing"
---

# PDF and document extraction (tables, text, OCR)

Extract data from PDFs and images with pay-per-use Apify Actors: tables to rows (bank statements, invoices, reports, ready for CSV or Excel), text page by page for RAG and search, and OCR for scanned PDFs and images in 100+ languages.

Disclosure: the routed Actors are built and sold by the skill author (Rowfeed); you pay per result on Apify, no subscription.

## Example prompts

Prompts this skill handles:

- "Convert these 12 bank statement PDFs into one CSV of transactions"
- "Extract the text of this 300-page PDF page by page so I can search it"
- "OCR these scanned German invoices and give me the text"

Out of scope (the boundary):

- "Fill in this PDF form for me" — this skill reads documents; it does not edit or fill them.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Pick the Actor from the routing table for the user's need.
2. Fetch its input schema (`apify actors info ACTOR_ID --input --json`) and build the input. Every Actor takes a list, so batch the user's items into one run.
3. Tell the user the estimated cost before large runs (the price per event is on the Actor's Store page) and cap spend with `maxTotalChargeUsd`.
4. Run, then summarise the rows returned and give the dataset link.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Tables in PDFs to rows | `rowfeed/pdf-table-extractor` | community | Bank statements, invoices, reports; one row per table row with page number |
| Text of PDFs page by page | `rowfeed/pdf-page-text-extractor` | community | Digital PDFs, page-level text for RAG and search |
| Scanned PDFs and images (OCR) | `rowfeed/image-to-text-ocr` | community | Tesseract OCR, 100+ languages, page by page |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling Actors — choose your interface

### Option A: Apify CLI (recommended for portability)

    apify actors call "rowfeed/pdf-table-extractor" \
      -i '{"pdfs":["https://example.com/statement.pdf"],"mode":"auto"}' \
      --json \
      --user-agent apify-awesome-skills/apify-pdf-documents \
      2>/dev/null

    # Fetch results
    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-pdf-documents 2>/dev/null

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>, for example `https://mcp.apify.com?tools=rowfeed/pdf-table-extractor,rowfeed/pdf-page-text-extractor,rowfeed/image-to-text-ocr`.
Documented at <https://docs.apify.com/platform/integrations/mcp>.

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Troubleshooting

- PDFs must be reachable by URL (public or signed link); password-protected files are reported, not charged.
- Use OCR only for scans; digital PDFs are faster and cheaper with the text extractor.
- A row with `error` and `errorMessage` was not charged; the message says what to fix.
