# Phase 1 Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Phase 1 MVP runtime skeleton for Autogenesis Agent with CLI, local API, session persistence, resource registry, trace store, tool runtime, and a deterministic agent loop.

**Architecture:** Use a Python package with clear module boundaries inspired by Hermes Agent's single reusable runtime and OpenClaw's separated control/session concepts. Phase 1 implements stable execution and observability only; SEPL self-evolution remains stubbed behind interfaces for Phase 2.

**Tech Stack:** Python 3.11+, stdlib SQLite, pytest, FastAPI optional local API, Typer optional CLI, JSON-serializable dataclasses.

---

## File Structure

- `pyproject.toml`: package metadata, test config, CLI entry point.
- `README.md`: local setup, architecture summary, commands.
- `.gitignore`: Python/runtime artifacts.
- `src/autogenesis_agent/__init__.py`: package exports.
- `src/autogenesis_agent/domain.py`: shared dataclasses and enums.
- `src/autogenesis_agent/storage.py`: SQLite schema and connection helpers.
- `src/autogenesis_agent/sessions.py`: session creation, message append, history retrieval.
- `src/autogenesis_agent/resources.py`: RSPL resource registry and version manager.
- `src/autogenesis_agent/tracing.py`: trace and tool-call persistence.
- `src/autogenesis_agent/tools.py`: tool registry, permission levels, deterministic built-in tools.
- `src/autogenesis_agent/runtime.py`: deterministic Phase 1 agent runtime loop.
- `src/autogenesis_agent/cli.py`: CLI entry point.
- `src/autogenesis_agent/api.py`: local API app factory.
- `tests/test_sessions.py`: session behavior.
- `tests/test_resources.py`: resource version behavior.
- `tests/test_runtime.py`: runtime, tool, trace behavior.
- `tests/test_api.py`: local API smoke behavior.

## Task 1: Project Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `README.md`
- Create: `src/autogenesis_agent/__init__.py`

- [ ] **Step 1: Write package metadata and empty package**
- [ ] **Step 2: Run `python3 -m pytest` and confirm collection works or fails only because tests do not exist**
- [ ] **Step 3: Commit skeleton**

## Task 2: Session Store

**Files:**
- Create: `src/autogenesis_agent/domain.py`
- Create: `src/autogenesis_agent/storage.py`
- Create: `src/autogenesis_agent/sessions.py`
- Test: `tests/test_sessions.py`

- [ ] **Step 1: Write failing tests for session creation and message history order**
- [ ] **Step 2: Run `python3 -m pytest tests/test_sessions.py -v` and verify failure**
- [ ] **Step 3: Implement SQLite schema and SessionManager**
- [ ] **Step 4: Run session tests and verify pass**
- [ ] **Step 5: Commit session store**

## Task 3: RSPL Resource Registry

**Files:**
- Create: `src/autogenesis_agent/resources.py`
- Test: `tests/test_resources.py`

- [ ] **Step 1: Write failing tests for resource registration, version lineage, and active version lookup**
- [ ] **Step 2: Run `python3 -m pytest tests/test_resources.py -v` and verify failure**
- [ ] **Step 3: Implement ResourceRegistry**
- [ ] **Step 4: Run resource tests and verify pass**
- [ ] **Step 5: Commit registry**

## Task 4: Tool Runtime and Trace Store

**Files:**
- Create: `src/autogenesis_agent/tools.py`
- Create: `src/autogenesis_agent/tracing.py`
- Test: `tests/test_runtime.py`

- [ ] **Step 1: Write failing tests for tool permission metadata, echo tool execution, and trace persistence**
- [ ] **Step 2: Run `python3 -m pytest tests/test_runtime.py -v` and verify failure**
- [ ] **Step 3: Implement ToolRegistry, built-in echo/search tools, TraceStore**
- [ ] **Step 4: Run runtime tests and verify pass**
- [ ] **Step 5: Commit tool and trace runtime**

## Task 5: Agent Runtime

**Files:**
- Create: `src/autogenesis_agent/runtime.py`
- Modify: `tests/test_runtime.py`

- [ ] **Step 1: Add failing test for deterministic runtime response and persisted trace**
- [ ] **Step 2: Run `python3 -m pytest tests/test_runtime.py -v` and verify failure**
- [ ] **Step 3: Implement AgentRuntime with prompt/resource/session/tool boundaries**
- [ ] **Step 4: Run runtime tests and verify pass**
- [ ] **Step 5: Commit runtime loop**

## Task 6: CLI and Local API

**Files:**
- Create: `src/autogenesis_agent/cli.py`
- Create: `src/autogenesis_agent/api.py`
- Test: `tests/test_api.py`
- Modify: `README.md`

- [ ] **Step 1: Write failing API smoke test**
- [ ] **Step 2: Run `python3 -m pytest tests/test_api.py -v` and verify failure**
- [ ] **Step 3: Implement CLI and FastAPI app factory with optional dependency guard**
- [ ] **Step 4: Run all tests**
- [ ] **Step 5: Commit CLI/API**

## Self-Review

- Spec coverage: Phase 1 P0 items are covered: runtime, sessions, tools, resource registry, trace store, CLI, local API.
- Exclusions: SEPL optimizer, Web UI, IM Gateway, MCP, multi-agent bus, deployment automation.
- Safety: Tool permissions are represented but high-risk side effects are not implemented.
