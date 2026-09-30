# LLM layer via the Apify OpenRouter Actor

Adding an LLM transformation between two sub-Actors (or as a final formatting step) is a common orchestrator pattern. Use the [Apify OpenRouter Actor](https://apify.com/apify/openrouter) as the LLM gateway — it exposes 300+ models via a single OpenAI-compatible endpoint and is billed through your Apify account.

> **The OpenRouter Actor is a Standby-mode Actor.** It exposes HTTP endpoints, not a start/wait Run cycle. **Do NOT** do `client.actor('apify/openrouter').call(...)` and expect a dataset — you'll get an empty dataset from the Standby container. Hit the HTTP URL directly with `fetch()`.

## Endpoint at a glance

- **Base URL:** `https://openrouter.apify.actor/api/v1`
- **Auth header:** `Authorization: Bearer $APIFY_TOKEN` (your normal Apify token)

| Method | Path | Purpose |
|---|---|---|
| POST | `/chat/completions` | OpenAI-format chat completions |
| POST | `/messages` | Anthropic-format messages |
| POST | `/embeddings` | Text embeddings |
| GET | `/models` | List available models |
| GET | `/providers` | List available providers |

Billing = Apify Standby usage (small) + the model's own token cost. The Actor page on the Apify Store shows current per-model pricing.

## Minimal TypeScript call

```typescript
import { log } from 'apify';

interface OpenRouterMessage {
    role: 'system' | 'user' | 'assistant';
    content: string;
}

async function callOpenRouter(messages: OpenRouterMessage[], model = 'openrouter/auto') {
    const res = await fetch('https://openrouter.apify.actor/api/v1/chat/completions', {
        method: 'POST',
        headers: {
            'content-type': 'application/json',
            Authorization: `Bearer ${process.env.APIFY_TOKEN}`,
        },
        body: JSON.stringify({ model, messages }),
    });
    if (!res.ok) {
        throw new Error(`OpenRouter ${res.status}: ${await res.text()}`);
    }
    const json = await res.json();
    log.info('OpenRouter usage', json.usage);
    return json.choices[0].message.content as string;
}
```

Usage in an orchestrator step:

```typescript
const runA = await client.actor('apify/website-content-crawler').call('crawl', { ... });
const items = await client.dataset(runA.defaultDatasetId).listItems({ skipEmpty: true });

const summary = await callOpenRouter([
    { role: 'system', content: 'You summarize scraped web pages in one paragraph.' },
    { role: 'user', content: items.items.map(i => i.text).join('\n---\n').slice(0, 12000) },
]);

await Actor.pushData({ summary, source: items.items.map(i => i.url) });
```

## Model choice

- `openrouter/auto` — router picks a model per request (cheapest reasonable choice).
- `anthropic/claude-sonnet-4-5` — high-quality general.
- `openai/gpt-4o-mini` — cheap and fast for classification/extraction.
- `google/gemini-2.5-flash` — cheap with long context.
- `GET /models` returns the full live list.

## Streaming

Add `stream: true` to the body. The response is Server-Sent Events (SSE). The final chunk carries the `usage` field.

## Common orchestrator patterns

- **Between steps** — Actor A scrapes, LLM classifies each item into buckets, Actor B is called once per bucket with different inputs.
- **As final formatting** — After the last sub-Actor, run each dataset item through the LLM to normalize it (e.g., extract structured fields from free text).
- **As a routing decision** — Ask the LLM which of N Actors to call next based on the user's original query.

## Gotchas

- **It's Standby, not Run.** Repeat: don't `client.actor('apify/openrouter').call(...)` — hit the HTTPS URL.
- **Token lives in your env**, not the orchestrator library. On the Apify platform `APIFY_TOKEN` is populated automatically; locally you set it (or run `apify login` and export it manually for scripts that don't use the SDK).
- **Rate limits & context windows** are per-model. Check the model's page on OpenRouter for the exact limit.
- **Cost visibility** — track `json.usage.total_tokens` and log it. LLM steps can silently dominate the run's cost.
