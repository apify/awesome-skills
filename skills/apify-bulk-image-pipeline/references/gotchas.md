# Gotchas — cost guardrails and recovery

## Cost guardrails

- **Quote before big batches.** Prices are flat per delivered item, so the estimate is exact: `n × $0.01` (generate), `n × $0.012` (upscale ≤ 4 MP), `n × $0.005` (cutout), `seconds × $0.05–0.06` (video). Video is the expensive step: 100 five-second clips is $25–30 — always confirm.
- **Caps are built in.** `maxPrompts`, `maxImages`, `maxVideos` bound each run, and the Apify run option "maximum cost per run" makes the Actor stop cleanly at the limit, reporting what remains unprocessed instead of failing.
- **Failures are free, so retries are cheap.** Only delivered results are billed. Rerunning a batch where 10 of 200 items failed costs only the retried successes — resend only the failed inputs, not the whole list.
- **Megapixel surcharges.** Generation above 1.1 MP and upscaling output above 4 MP bill extra per started megapixel. A 4x upscale of a 1000×1000 photo is 16 MP = 12 extra megapixels ($0.024 extra). For bulk work, `maxOutputMegapixels` (default 16) is the safety net; lower it if you only need web sizes.
- **Skips are free.** `skipIfLongEdgeAtLeast` (upscaler) returns already-large images untouched at no charge — use it whenever rerunning over a mixed folder.

## Recovery patterns

- **Partial failure in a batch** → filter the dataset for `"status": "error"`, collect their `inputUrl`/`prompt`, and rerun with only those. Items are in input order, so mapping back is positional (`index`).
- **Run stopped at its cost cap** → the run log names how many inputs remain. Resend just the tail of the list.
- **Google Drive link fails** → the item's `error` says the file answered with a web page: the file is not shared "anyone with the link". Fix sharing or download and re-upload. Private Drive OAuth is not supported.
- **Video rejects an image** → below the 256×256 floor; run `sherwood/image-upscaler-batch` on it first (that floor is why the two chain well).
- **Safety checker flagged a prompt/clip** → free error item with the reason. Rephrase the prompt; the models' content rules cannot be bypassed through these Actors.
- **Same image needed again** → generation items carry `seed`; same prompt + same `seed` reproduces the image instead of paying for variations hunting.

## Chaining notes

- Every Actor accepts `datasetId` (+ `urlField` when auto-detection misses the image field, e.g. `images[].url`), so pipeline steps connect without downloading anything.
- `keepFields` (upscaler) copies chosen fields (SKU, listing URL) from source items into results under `source`, and `sourceItemIndex` preserves the mapping — spreadsheets reconcile without extra work.
- For an always-on pipeline, schedule the first Actor and wire the next ones from the Apify **Integrations** tab with `{"datasetId": "{{resource.defaultDatasetId}}"}`.
