---
name: apify-bulk-image-pipeline
description: Turn a list of prompts, image URLs or another Actor's dataset into finished visuals in bulk — generate images with FLUX (text to image), upscale them 2x/4x or to 4K with SeedVR2 super-resolution, remove backgrounds into transparent cutouts, and animate images into short mp4 clips with MiniMax Hailuo — each step one Apify Actor call, chainable by datasetId, billed per delivered result with failures free and no model API key. Use when the user says "generate images in bulk from prompts", "turn this CSV / Google Sheet of prompts into images", "upscale a folder or list of images", "enhance image quality / increase resolution", "upscale to 4K", "remove backgrounds in bulk", "animate these product photos", "turn photos into videos", "image to video API", "make thumbnails for my content calendar", or wants a generate → upscale → cutout → video pipeline without managing fal, FLUX, SeedVR2 or MiniMax accounts.
author: Sherwood Tools
author_url: https://github.com/maxouf
metadata:
  category: data-extraction
  keywords: "image-generation, flux, text-to-image, image-upscaler, seedvr2, super-resolution, upscale-4k, enhance-image-quality, background-removal, transparent-png, image-to-video, minimax-hailuo, animate-photos, bulk-images, batch-processing, product-photos, thumbnails, media-pipeline"
---

# Bulk Image Pipeline (generate, upscale, cut out, animate)

Produce visuals in bulk with four chainable Apify Actors: FLUX image generation, SeedVR2 upscaling, background removal, and MiniMax Hailuo image-to-video. Every Actor takes a list (or another Actor's `datasetId`), returns one dataset item per input with `status`/`error`, bills only delivered results, and needs no model API key.

> Disclosure: the routed `sherwood/*` Actors are built by this skill's author. The two scraper rows in the routing table are unaffiliated.

## Example prompts

Prompts this skill handles:

- "Here are 40 prompts in a CSV — generate one 16:9 image per prompt and give me the URLs."
- "Upscale all the images in this dataset to 4K without losing quality."
- "Take these 12 product photos, remove the backgrounds, then animate each one with a slow 360 rotation."

Out of scope (the boundary):

- "Edit this specific image's content" (inpainting, object removal, style transfer) — these Actors generate, enlarge, cut out and animate; they do not edit image content. Search the Apify Store for image-editing Actors instead.

## Prerequisites

- Apify account ([sign up](https://apify.com)) — the free plan's monthly $5 credit covers roughly 500 generated images, 400 upscales or 100 seconds of video
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. **Pick the step(s)** from the routing table: generate, upscale, cut out, animate — or a chain of them.
2. **Build the input.** Every Actor accepts a plain list (`prompts` or `imageUrls`), a single string (comma or newline separated), Google Drive / Dropbox share links, base64, or `datasetId` + optional `urlField` to read another Actor's output. Nothing is required; the default input is a safe sample run.
3. **Estimate cost and confirm.** Price per delivered item is fixed (table below). For more than ~50 items or any video work, state the estimate before running (`n images × $0.01`, `n seconds × $0.06`) and respect any budget the user gave via `maxImages` / `maxVideos` or the run's max cost.
4. **Run and deliver.** Each run returns one dataset item per input, in order, with `outputUrl`, dimensions and `status`. Report delivered / failed counts and the failure reasons (items with `"status": "error"` are free). To chain, pass the finished run's `defaultDatasetId` as the next Actor's `datasetId`.

## Actor routing

| User need | Actor ID | Tier | Price (Free plan) | Best for |
|-----------|----------|------|-------------------|----------|
| Text to image, bulk | `sherwood/image-generator-batch` | community | $0.01 / image (1024×1024) | FLUX.2 Klein; prompt lists, thumbnails, product mock-ups; `seed` for reproducibility |
| Upscale / enhance quality | `sherwood/image-upscaler-batch` | community | $0.012 / image (≤ 4 MP) | SeedVR2 super-resolution 2x/4x or `targetLongEdge` (3840 = 4K); skips already-large images free |
| Remove background | `sherwood/background-remover-batch` | community | $0.005 / image | Transparent PNG/WebP cutouts for e-commerce and design |
| Image/text to video | `sherwood/video-generator-batch` | community | $0.05 / second delivered | MiniMax Hailuo mp4 clips, 1–15 s, optional end-frame keyframe |
| Source images from Instagram | `apify/instagram-scraper` | apify | per result | Feed scraped post images into the pipeline via `datasetId` |
| Source images from Google Maps | `compass/crawler-google-places` | community | per place | Feed place photos into the pipeline via `datasetId` |

`Tier` = `apify` (Apify-maintained) or `community` (third-party).

## Calling the Actors

### Generate (text to image)

    apify actors call "sherwood/image-generator-batch" \
      -i '{"prompts": ["A ceramic coffee mug on a wooden table, product photography"], "imageSize": "landscape_16_9"}' \
      --json \
      --user-agent apify-awesome-skills/apify-bulk-image-pipeline \
      2>/dev/null

Key fields: `prompts` (array or newline-separated string), `imageSize` (`square_hd`, `landscape_16_9`, `portrait_16_9`...), `quality` (`standard` = FLUX.2 Klein, `fast` = FLUX Schnell for drafts), `imagesPerPrompt` (1–4), `seed`, `maxPrompts`.

### Upscale (super-resolution)

    apify actors call "sherwood/image-upscaler-batch" \
      -i '{"imageUrls": ["https://example.com/a.jpg"], "targetLongEdge": 2048, "outputFormat": "png"}' \
      --json \
      --user-agent apify-awesome-skills/apify-bulk-image-pipeline \
      2>/dev/null

Key fields: `imageUrls` (URLs, Drive/Dropbox links, base64), `scale` (`"2"`/`"4"`) or `targetLongEdge` (pixels, 3840 = 4K), `skipIfLongEdgeAtLeast` (free skip of already-large images), `datasetId` + `urlField` + `keepFields` to chain, `maxImages`.

### Remove background

    apify actors call "sherwood/background-remover-batch" \
      -i '{"imageUrls": ["https://example.com/product.jpg"]}' \
      --json \
      --user-agent apify-awesome-skills/apify-bulk-image-pipeline \
      2>/dev/null

Output is a transparent PNG (or WebP) per image; same input tolerance and chaining as the upscaler.

### Animate (image/text to video)

    apify actors call "sherwood/video-generator-batch" \
      -i '{"imageUrls": ["https://example.com/product.jpg"], "prompts": ["Slow 360 rotation, studio lighting"], "duration": 5}' \
      --json \
      --user-agent apify-awesome-skills/apify-bulk-image-pipeline \
      2>/dev/null

`prompts` and `imageUrls` are paired by index; a list of one is reused for every clip. `endImageUrls` pins the last frame. Input images below 256×256 come back as free error items — upscale them first.

### Chain two steps

Take `defaultDatasetId` from the first run's JSON, then:

    apify actors call "sherwood/image-upscaler-batch" \
      -i '{"datasetId": "DATASET_ID_FROM_STEP_1", "targetLongEdge": 2048}' \
      --json \
      --user-agent apify-awesome-skills/apify-bulk-image-pipeline \
      2>/dev/null

### Fetch results

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-bulk-image-pipeline \
      2>/dev/null

Full routing details: [references/actor-index.md](references/actor-index.md).

## Troubleshooting

- Item has `"status": "error"` with a reason (dead URL, not an image, safety checker) → it was free; fix or drop that input and rerun only the failures.
- Google Drive link comes back as an error → the file is not shared "anyone with the link"; private Drive (OAuth) is not supported.
- Video input rejected for size → MiniMax needs ≥ 256×256; run the upscaler on it first.
- Run stopped early with items remaining → the run hit its max cost; the log says how many inputs remain. Raise the cap or rerun — finished items are not re-billed when you resend only the remaining inputs.
- For cost guardrails and recovery patterns, see [references/gotchas.md](references/gotchas.md).
