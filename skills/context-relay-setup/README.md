# Context Relay Setup

> Give your agent a spa day for its brain. Declutter the chaos, boost its "management IQ", and make sure it never forgets what it promised.

A one-time setup that teaches your agent to maintain memory continuity across broken execution boundaries — sessions, cron jobs, sub-agents, and heartbeat.

**Install once, delete the folder.** The framework lives in your agent's core MDs after setup.

## The Problem

OpenClaw agents lose context at multiple points:

| Break Point | What Happens |
|-------------|-------------|
| **Session restart** | Context window clears, previous conversation forgotten |
| **Sub-agent boundary** | Child agents are isolated processes, no inherited memory |
| **Cron isolation** | Scheduled tasks run in isolated sessions, no conversation context |
| **Heartbeat isolation** | Same as cron |
| **Context compression** | Long conversations get compressed, details lost |

Without Context Relay, agents repeatedly ask "what were we talking about?" or make wrong decisions in cron tasks due to missing context.

## Core Principle

**Files are the single source of truth.** Don't rely on session memory. Don't assume "I should remember." Every execution unit (session, cron, sub-agent, heartbeat) reads context from files on startup.

## What This Skill Does

This is **not** a callable tool. It's a **framework** that integrates into your agent's core documentation:

1. **Context Relay mechanism** — teaches the agent to read/write context files at execution boundaries
2. **Self-todo system (todos.json)** — bridges conversation promises to heartbeat execution
3. **Project management patterns** — structured directories with machine-readable state + human-readable decisions

## Installation

See [SKILL.md](./SKILL.md) for detailed installation steps. In summary:

1. Create `workspace/todos.json` (empty todo file)
2. Add Context Relay sections to your agent's core documentation (AGENTS.md or equivalent)
3. Add todo pickup logic to your HEARTBEAT.md
4. Register `todos.json` in your workspace file table

Template files are provided in `templates/` to bootstrap new projects and empty todo files.

## File Structure

```
context-relay/
├── SKILL.md                              # Full installation guide
├── README.md                             # This file
└── templates/
    ├── todos.json                        # Empty todo file
    └── project-scaffold/
        ├── PROJECT.md                    # Project definition template
        └── context/
            ├── state.json                # Machine-readable state
            └── decisions.md              # Human-readable decision log
```

## Design Philosophy

1. **Files > Memory** — Don't trust session context, persist everything to files
2. **Explicit > Implicit** — Cron/sub-agent/heartbeat must explicitly declare which files to read
3. **Do it now > Do it later** — Todos are a fallback mechanism, not the default workflow
4. **State + Decisions separation** — `state.json` for machines (fast recovery), `decisions.md` for humans (understanding why)

## For OpenClaw

This skill is designed for [OpenClaw](https://github.com/openclaw/openclaw) agents but the patterns are applicable to any AI agent system that deals with:
- Multiple execution contexts (sessions, background tasks, sub-agents)
- Persistent state management
- Task handoff between isolated processes

## License

MIT
