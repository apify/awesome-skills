# Connecting each client to the Apify MCP server

All clients point at the same endpoint. Narrowing to one Actor is optional but makes
tool selection more reliable when product data is the only job:

```
https://mcp.apify.com?tools=apify/e-commerce-scraping-tool
```

Dropping `?tools=` lets the agent search all of Apify Store at runtime. That is a
trade rather than an upgrade: it buys a fallback for retailers this Actor cannot read,
and it costs tool-selection reliability, because the model then chooses from tens of
thousands of Actors instead of one. Narrow it when product data is the whole job, and
open it up only if you actually need the fallback.

Either way, a retailer missing from the Actor's `marketplaces` list is not a reason to
reach for another Actor: generic extraction is on by default, so unlisted sites often
work. Try this Actor first.

## Contents

- [Claude Desktop](#claude-desktop)
- [Claude Code](#claude-code)
- [Cursor](#cursor)
- [n8n](#n8n)
- [Any other MCP client](#any-other-mcp-client)
- [Python, with the official SDK](#python-with-the-official-sdk)
- [Verifying the connection](#verifying-the-connection)

## Claude Desktop

Claude Desktop adds remote MCP servers as custom connectors, not through
`claude_desktop_config.json`. Open **Settings → Connectors**, choose **Add custom
connector**, and enter the endpoint above. Complete OAuth when Claude prompts. See
[Apify's Claude integration guide](https://docs.apify.com/integrations/claude) and
[Claude's custom connector guide](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).

## Claude Code

Add the Streamable HTTP server to the current project:

```bash
claude mcp add --transport http --scope project apify-ecommerce \
  'https://mcp.apify.com?tools=apify/e-commerce-scraping-tool'
```

The equivalent project configuration includes the transport type explicitly:

```json
{
  "mcpServers": {
    "apify-ecommerce": {
      "type": "http",
      "url": "https://mcp.apify.com?tools=apify/e-commerce-scraping-tool"
    }
  }
}
```

## Cursor

`.cursor/mcp.json` in the project, or `~/.cursor/mcp.json` for every project:

```json
{
  "mcpServers": {
    "apify-ecommerce": {
      "url": "https://mcp.apify.com?tools=apify/e-commerce-scraping-tool"
    }
  }
}
```

## n8n

There is no JSON to copy, because MCP is a node rather than a config file.

1. Add an **AI Agent** node.
2. Attach an **MCP Client Tool** to it.
3. Set the endpoint to the URL above.
4. Authenticate with a bearer token from Apify Console, not OAuth, because the node
   runs unattended with nobody present to approve a browser prompt.

## Any other MCP client

Anything speaking **Streamable HTTP** works against the same URL. SSE was removed on
April 1, 2026, so a client that only speaks SSE will fail to connect.

## Python, with the official SDK

Requires Python 3.10 or newer. The SDK does not take headers directly, so pass an
authenticated HTTP client:

```python
import asyncio
import json
import re

import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

URL = "https://mcp.apify.com?tools=apify/e-commerce-scraping-tool"

TERMINAL_FAILURES = {"FAILED", "ABORTED", "TIMED-OUT", "TIMED_OUT"}
ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def parse_tool_json(result, tool_name):
    if result.is_error:
        raise RuntimeError(f"{tool_name} returned an error")
    for block in result.content:
        text = getattr(block, "text", None)
        if text:
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                continue
    raise RuntimeError(f"{tool_name} returned no JSON payload")


def require_id(value, label):
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        raise RuntimeError(f"{label} is missing or invalid")
    return value


def require_object(value, tool_name):
    if not isinstance(value, dict):
        raise RuntimeError(f"{tool_name} returned invalid metadata")
    return value


async def _fetch_products(
    *, token, actor_input, poll_wait_seconds, deadline_seconds, result_limit, run_state
):
    async with httpx2.AsyncClient(
        headers={"Authorization": f"Bearer {token}"},
        timeout=deadline_seconds,
    ) as http:
        async with streamable_http_client(URL, http_client=http) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                result = await session.call_tool(
                    "apify--e-commerce-scraping-tool", actor_input
                )
                meta = require_object(parse_tool_json(result, "Actor tool"), "Actor tool")
                run_id = require_id(meta.get("runId") or meta.get("id"), "run id")
                run_state["run_id"] = run_id
                while str(meta.get("status", "")).upper() != "SUCCEEDED":
                    status = str(meta.get("status", "")).upper()
                    if status in TERMINAL_FAILURES:
                        raise RuntimeError(f"Actor run ended with status {status}")
                    await asyncio.sleep(poll_wait_seconds)
                    result = await session.call_tool(
                        "get-actor-run", {"runId": run_id}
                    )
                    meta = require_object(
                        parse_tool_json(result, "get-actor-run"), "get-actor-run"
                    )
                    if require_id(meta.get("runId") or meta.get("id"), "run id") != run_id:
                        raise RuntimeError("get-actor-run returned a different run id")

                dataset_id = require_id(
                    meta.get("datasetId")
                    or meta.get("storages", {})
                    .get("datasets", {})
                    .get("default", {})
                    .get("id"),
                    "dataset id",
                )
                result = await session.call_tool(
                    "get-dataset-items",
                    {"datasetId": dataset_id, "limit": result_limit},
                )
                return parse_tool_json(result, "get-dataset-items")


async def fetch_products(
    *, token, actor_input, poll_wait_seconds, deadline_seconds, result_limit
):
    if not token or not isinstance(actor_input, dict):
        raise ValueError("token and actor_input are required")
    if poll_wait_seconds <= 0 or deadline_seconds <= 0:
        raise ValueError("poll interval and deadline must be positive")
    if isinstance(result_limit, bool) or not isinstance(result_limit, int) or result_limit <= 0:
        raise ValueError("result limit must be a positive integer")
    actor_cap = actor_input.get("maxProductResults")
    if isinstance(actor_cap, bool) or not isinstance(actor_cap, int) or actor_cap <= 0:
        raise ValueError("actor_input.maxProductResults must be a positive integer")
    run_state = {}
    try:
        return await asyncio.wait_for(
            _fetch_products(
                token=token,
                actor_input=actor_input,
                poll_wait_seconds=poll_wait_seconds,
                deadline_seconds=deadline_seconds,
                result_limit=result_limit,
                run_state=run_state,
            ),
            timeout=deadline_seconds,
        )
    except TimeoutError:
        run_id = run_state.get("run_id")
        if run_id:
            raise TimeoutError(
                f"Stopped waiting for run {run_id}; it may still be active. "
                "Resume with get-actor-run; do not start another run."
            ) from None
        raise TimeoutError(
            "Timed out before a run ID was captured; dispatch is unconfirmed. "
            "Inspect account runs before any retry."
        ) from None
```

This example targets the verified `mcp` 2.2 API and uses its snake_case result attribute
`is_error`.

`maxProductResults` caps Actor output; `result_limit` only caps the dataset read.
The caller deadline stops waiting, not the remote Actor. Keep the run ID from a
timeout error and resume polling it instead of paying for another start. Neither
limit is a platform spend cap.

## Verifying the connection

Ask the client to list its tools. A working connection shows five:

```
apify--e-commerce-scraping-tool
get-actor-run
get-dataset-items
get-key-value-store-record
abort-actor-run
```

The helper tools arrive even when `?tools=` narrows the list, because the Actor tool
alone cannot deliver products: `get-actor-run` waits for the run to finish and
`get-dataset-items` reads the output.

### Gotcha

If only the helper tools appear and the Actor is missing, the `?tools=` value is
probably wrong. It takes the Actor id with a slash (`apify/e-commerce-scraping-tool`),
while the tool it produces is named with two hyphens
(`apify--e-commerce-scraping-tool`). Mixing the two forms silently yields a connection
with no Actor on it.
