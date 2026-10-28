# Actor index — bulk image pipeline

Full routing table with inputs, outputs and chaining notes. Prices shown are Free-plan prices; volume plans pay the same or less — each Actor's Store page shows the exact tier table.

## sherwood/image-generator-batch — Bulk AI Image Generator (FLUX)

- **Store**: https://apify.com/sherwood/image-generator-batch
- **Price**: $0.01 per delivered image up to 1024×1024; +$0.01 per started megapixel above 1.1 MP for custom sizes. Failures and safety-flagged prompts free.
- **Input**: `prompts` (array; aliases `prompt`, `texts`, `queries`; newline-separated strings split), `imageSize` preset or exact `width`/`height` (256–2048), `quality` (`standard` = FLUX.2 Klein 9B, `fast` = FLUX Schnell), `imagesPerPrompt` (1–4), `outputFormat` (`png`/`jpeg`/`webp`), `seed`, `maxPrompts`.
- **Output item**: `index`, `variant`, `prompt`, `outputUrl`, `width`, `height`, `seed`, `model`, `format`, `durationMs`, `status`, `error`.
- **Chain out**: pass the run's `defaultDatasetId` to the upscaler, background remover or video generator.

## sherwood/image-upscaler-batch — AI Image Upscaler (SeedVR2)

- **Store**: https://apify.com/sherwood/image-upscaler-batch
- **Price**: $0.012 per delivered image with output up to 4 MP; +$0.002 per started megapixel above. Failures and skips free.
- **Input**: `imageUrls` (URLs, Google Drive/Dropbox share links, Drive file IDs, base64/data URIs, console uploads via `imageFiles`; aliases `imageUrl`, `urls`, `images`, `startUrls`), `scale` (`"2"`/`"4"`) or `targetLongEdge` (px; 3840 = 4K; max 4x), `skipIfLongEdgeAtLeast`, `outputFormat` (`jpg`/`png`/`webp`, PNG/WebP keep transparency), `maxOutputMegapixels`, `maxImages`; `datasetId` + `urlField` + `maxImagesPerItem` + `keepFields` to read another Actor's output.
- **Output item**: `index`, `inputUrl`, `outputUrl`, `width`, `height`, `megapixels`, `scale`, `factor`, `format`, `model`, `durationMs`, `status` (`ok`/`error`/`skipped`), `error`; `sourceItemIndex` and `source` when chained.
- **Chain out**: `defaultDatasetId` to the background remover or video generator.

## sherwood/background-remover-batch — Background Remover API

- **Store**: https://apify.com/sherwood/background-remover-batch
- **Price**: $0.005 per delivered cutout. Failures free.
- **Input**: same tolerant image inputs as the upscaler (`imageUrls` + aliases, Drive/Dropbox, base64, uploads, `datasetId`), `outputFormat` (`png`/`webp`, transparent).
- **Output item**: one transparent cutout per image with `inputUrl`, `outputUrl`, dimensions, `status`, `error`.
- **Chain out**: cutouts into the upscaler (transparency survives in PNG/WebP) or the video generator.

## sherwood/video-generator-batch — Image to Video API (MiniMax Hailuo)

- **Store**: https://apify.com/sherwood/video-generator-batch
- **Price**: $0.05–$0.06 per second of delivered video depending on plan (5-s clip ≈ $0.25–$0.30), billed on measured delivered duration. Failed clips free. All resolutions cost the same.
- **Input**: `imageUrls` (first frames; same tolerant forms as above) and/or `prompts` (paired by index; a list of one is reused), `endImageUrls` (last-frame keyframes), `duration` (1–15 s), `resolution` (`768P`/`1080P`/`480P`), `promptExpansion`, `seed`, `maxVideos`; `datasetId` + `urlField` to animate another Actor's images.
- **Output item**: `index`, `prompt`, `imageUrl`, `outputUrl` (mp4), `durationSeconds` (measured), `billedSeconds`, `resolution`, `fileSize`, `model`, `status`, `error`.
- **Constraint**: input images ≥ 256×256 (smaller = free error item; upscale first). No audio track.

## Unaffiliated sources (feed the pipeline)

- `apify/instagram-scraper` — post and profile images; chain with `datasetId` + `urlField` (e.g. `images[].url`).
- `compass/crawler-google-places` — place photos from Google Maps; chain the images field the same way.
