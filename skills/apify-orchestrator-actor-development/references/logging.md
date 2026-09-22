# Actor logging reference

**ALWAYS use the `apify/log` package for logging** — this package censors sensitive data (Apify tokens, API keys, credentials) and prevents accidental exposure in logs.

## Available log levels in `apify/log`

The Apify log package provides the following methods:

- `log.debug()` — Debug level logs (detailed diagnostic information)
- `log.info()` — Info level logs (general informational messages)
- `log.warning()` — Warning level logs (potentially problematic situations)
- `log.warningOnce()` — Warning logged only once for the same message
- `log.error()` — Error level logs (failures)
- `log.exception()` — Exception level logs (for exceptions with stack traces)
- `log.perf()` — Performance metrics and timing information
- `log.deprecated()` — Warnings about deprecated code
- `log.softFail()` — Non-critical failures that don't stop execution (e.g., input validation errors, skipped items)
- `log.internal()` — Internal/system messages

## Best practices

- Use `log.debug()` for detailed operation-level diagnostics
- Use `log.info()` for general informational messages (API requests, successful operations)
- Use `log.warning()` for potentially problematic situations (validation failures, unexpected states)
- Use `log.error()` for actual errors and failures
- Use `log.exception()` for caught exceptions with stack traces

## In an orchestrator Actor

Log each sub-Actor call with `log.info()` so the parent Run's log tells the story of the pipeline. The `apify-orchestrator` library also emits its own structured logs when `enableLogs: true` is passed to the `Orchestrator` constructor — you don't need to duplicate those.
