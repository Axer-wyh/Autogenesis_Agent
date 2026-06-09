# Autogenesis Agent

Autogenesis Agent is a Phase 1 MVP runtime for a controlled self-evolving agent platform. It starts with stable execution, resource versioning, trace capture, and local developer interfaces before adding SEPL self-evolution in later phases.

## Phase 1 Scope

- CLI entry point.
- Local API app factory.
- Session persistence with SQLite.
- RSPL-style resource registry and version manager.
- Tool registry with permission levels.
- Trace store for runtime and tool-call observability.
- Deterministic runtime loop for testable local execution.

## Architecture Reference

This implementation follows the product plan in `docs/product/autogenesis_agent_product_plan.md`.

The Phase 1 code intentionally borrows two practices:

- Hermes style: one reusable agent runtime that can be called by CLI, API, cron, or future gateways.
- OpenClaw style: keep gateway/session/control boundaries explicit from the start.

## Local Commands

Run tests:

```bash
python3 -m pytest
```

Run CLI:

```bash
python3 -m autogenesis_agent.cli "hello"
```
