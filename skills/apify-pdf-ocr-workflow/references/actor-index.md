# Actor index: PDF OCR workflow

The Actor this skill routes to. Financial interest: `tanod/pdf-ocr` is built and sold by the skill's author.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| PDF | Scanned PDF to searchable PDF plus plain text | `tanod/pdf-ocr` | community | Inputs: `urls` (required), `pages`, `language` (17 Tesseract codes, up to 3 joined with `+`), `dpi`, `skipPagesWithText`, `includeTextInDataset`. One dataset row per unique link. Billed per recognised page plus the Actor start event. |

## Not this Actor

| User intent | Why not | Instead |
|-------------|---------|---------|
| Tables from a PDF as CSV | OCR returns plain text, not table structure | Search the Store for a PDF table extraction Actor |
| Text from a PDF that already has a text layer | Nothing to recognise; selected pages with text incur no page charge; the start charge still applies | Any PDF text extraction Actor, or read the text layer directly |
| Scans in a language that is not installed | Other codes fail | Search the Store for an OCR Actor that lists the language |

## How to extend

1. Search candidates: `apify actors search "pdf ocr" --json --limit 20 --user-agent apify-awesome-skills/apify-pdf-ocr-workflow 2>/dev/null`
2. Fetch the input schema: `apify actors info "tanod/pdf-ocr" --input --user-agent apify-awesome-skills/apify-pdf-ocr-workflow 2>/dev/null`
3. Add a row above with the user intent that should trigger it.

`Tier` is `community`: a third-party Actor on the Apify Store, not Apify-maintained.
