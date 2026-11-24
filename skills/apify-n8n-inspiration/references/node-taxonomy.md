# n8n node taxonomy for the scout

Non-exhaustive patterns used by the classification step in SKILL.md. Match on the node's `name` field (stable), not `displayName` (user-editable). All matches are case-insensitive substring unless noted.

## LLM nodes (bucket 2 trigger)

| Vendor / family | Patterns |
|-----------------|----------|
| OpenAI | `openAi`, `openai`, `lmChatOpenAi`, `embeddingsOpenAi`, `openAiAssistant` |
| Anthropic | `anthropic`, `claude`, `lmChatAnthropic` |
| Google | `googleGemini`, `gemini`, `lmChatGoogleGemini`, `googlePalm`, `vertexAi` |
| Mistral | `mistral`, `lmChatMistralCloud` |
| Ollama (self-hosted) | `ollama`, `lmChatOllama`, `lmOllama` |
| Cohere | `cohere`, `lmChatCohere`, `embeddingsCohere` |
| DeepSeek | `deepseek`, `lmChatDeepSeek` |
| Groq | `groq`, `lmChatGroq` |
| Together | `together`, `lmChatTogether` |
| OpenRouter | `openrouter`, `lmChatOpenRouter` |
| LangChain generic | `@n8n/n8n-nodes-langchain.agent`, `@n8n/n8n-nodes-langchain.chainLlm`, `@n8n/n8n-nodes-langchain.lmChat*` |
| Local models (catch-all) | `llama`, `huggingFace`, `localAi` |

If a template contains a LangChain `agent` or `chainLlm` node, count it as an LLM node even if the specific model node is missing — the agent is driving the model.

## Apify nodes

| Pattern | Notes |
|---------|-------|
| `n8n-nodes-base.apify` | Official first-party Apify node (Actor run / dataset read / etc.). |
| `displayName` contains "Apify" | Catches community forks. |
| `n8n-nodes-base.httpRequest` with `parameters.url` matching `api.apify.com` | Common pattern because the first-party node lagged on some endpoints. |

## Infrastructure / trigger / utility (ignore for classification)

A workflow that is "only Apify + LLM + these" still counts as **Actor power-up** (bucket 2). A workflow that is "only non-Apify data node + these" still counts as **Marketing replica** (bucket 1).

- Triggers: `manualTrigger`, `scheduleTrigger`, `webhook`, `cron`, `respondToWebhook`, `emailTrigger`, `formTrigger`
- Control flow: `if`, `switch`, `merge`, `splitInBatches`, `splitOut`, `aggregate`, `filter`, `itemLists`, `wait`, `noOp`
- Data shaping: `set`, `code`, `function`, `html`, `markdown`, `extractFromFile`
- Documentation: `stickyNote`
- Internal: `executeWorkflow`, `executeCommand`

## Competitor scraper nodes (treated as scraper nodes with ⚠️ conversion flag)

Firecrawl, Bright Data, Exa, Airtop, ScrapingBee, Dumpling AI, Phantombuster — see [competitor-scrapers.md](competitor-scrapers.md) for the full patterns and the Apify Actor to pitch as the swap-in. These do **not** disqualify a template from the power-up or MCP-integration buckets.

## Service nodes that often appear but are NOT yet MCP-connector-supported

Route to **bucket 4 — Other / mixed** when they're the main non-scraper integration:

- Google: `googleSheets`, `gmail`, `googleDrive`, `googleCalendar`, `youTube`
- Microsoft: `microsoftOutlook`, `microsoftTeams`, `microsoftOneDrive`, `microsoftExcel`
- Email: `emailSend`, `sendInBlue`, `mailgun`
- CRM: `hubspot`, `salesforce`, `pipedrive`, `zoho`
- Comms: `discord`, `telegram`, `twilio`, `whatsapp`
- Storage / DB: `postgres`, `mysql`, `mongoDb`, `redis`, `airtable`
- E-commerce: `shopify`, `woocommerce`, `stripe`
- Social: `twitter`, `linkedIn`, `facebookGraphApi`

(When any of these move onto the MCP connector list, promote them to [apify-mcp-connectors.md](apify-mcp-connectors.md).)
