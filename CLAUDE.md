# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

This is a proxy server that routes Claude Code CLI/VSCode requests to alternative LLM providers (NVIDIA NIM, OpenRouter, LM Studio, llama.cpp). See [AGENTS.md](AGENTS.md) for detailed development workflow; see [README.md](README.md) for features and configuration.

## Development Commands

Run in order before committing:
```bash
uv run ruff format   # Format code
uv run ruff check    # Lint
uv run ty check      # Type check
uv run pytest        # Run tests
```

Run a single test: `uv run pytest tests/path/to/test_file.py::test_name -v`

Run the server: `uv run uvicorn server:app --host 0.0.0.0 --port 8082`

## Project Structure

```
├── server.py              # Entry point, imports app from api/
├── api/                   # FastAPI routes, request detection, optimization handlers
│   ├── app.py             # FastAPI app, lifespan, dependencies
│   ├── routes.py          # /v1/messages endpoint
│   ├── detection.py       # Request type detection (optimization, model routing)
│   └── optimization_handlers.py  # Local handlers for trivial requests
├── providers/             # LLM provider implementations
│   ├── base.py            # BaseProvider ABC, ProviderConfig
│   ├── openai_compat.py   # OpenAICompatibleProvider base class
│   ├── common/            # Shared utilities (SSE, message conversion, parsers)
│   ├── nvidia_nim/        # NVIDIA NIM provider
│   ├── open_router/       # OpenRouter provider
│   ├── lmstudio/          # LM Studio provider
│   └── llamacpp/          # llama.cpp provider
├── messaging/             # Discord/Telegram bot for remote control
│   └── platforms/         # MessagingPlatform ABC + Discord/Telegram implementations
├── cli/                   # CLI session management
├── config/                # Settings (pydantic-settings), logging
└── tests/                 # Pytest test suite (mirrors src structure)
```

## Architecture

### Provider Pattern
- `BaseProvider` defines `stream_response()` returning Anthropic SSE format
- `OpenAICompatibleProvider` extends BaseProvider for OpenAI-compatible APIs
- Providers translate Anthropic requests → OpenAI format → stream back as SSE
- Model routing: `MODEL_OPUS`/`MODEL_SONNET`/`MODEL_HAIKU` env vars; `MODEL` is fallback
- Format: `provider_prefix/model/name` (e.g., `nvidia_nim/moonshotai/kimi-k2.5`)

### Request Flow
1. Claude Code sends Anthropic-formatted request to `/v1/messages`
2. `detection.py` identifies request type (optimization vs real LLM call)
3. Optimization requests (quota probes, title gen, etc.) handled locally
4. Real requests routed to appropriate provider based on model prefix
5. Provider streams response in Anthropic SSE format

### Key Components
- **SSEBuilder**: Constructs Anthropic SSE events (message_start, content_block_delta, etc.)
- **ThinkTagParser**: Converts `<think>` tags and `reasoning_content` to Claude thinking blocks
- **HeuristicToolParser**: Parses tool calls emitted as text into structured tool use
- **GlobalRateLimiter**: Rolling-window rate limiting + exponential backoff for 429s

### Messaging Platform Pattern
- `MessagingPlatform` ABC in `messaging/platforms/base.py`
- Implementations: Discord, Telegram
- Enables remote Claude Code control via chat bots
- Session persistence, tree-based threading, live progress streaming

## Key Principles (from AGENTS.md)

- Extract common logic into `providers/common/` — no cross-provider imports
- Provider-specific config stays in provider constructors, not base `ProviderConfig`
- Use settings/config instead of hardcoded values
- No `# type: ignore` — fix the underlying type issue
- All 5 CI checks must pass: format, lint, type check, tests
