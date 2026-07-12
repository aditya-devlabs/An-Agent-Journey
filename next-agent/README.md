# nextjs-agent

An AI agent harness for Next.js projects. Reads, creates, modifies, deletes files, manages packages, and explores repositories — with git-based snapshots for safe approve/discard workflows.

## What It Does

You describe what you want built. The agent plans the work, executes it on a git branch, and shows you exactly what changed before you approve.

```
>>> Add a dark mode toggle

[Git]   Created branch: agent/add-dark-mode
[Agent] Plan:
        1. Create DarkModeToggle component
        2. Integrate into layout.tsx
        
        Proceed? [y/n/custom]

>>> y

[Agent] Creating component...
[Git]   Saved: "Add DarkModeToggle component"
[Agent] Editing layout.tsx...
[Git]   Saved: "Integrate DarkModeToggle"

[Done] 2 files changed
       [View Diff]  [Approve & Merge]  [Discard]
```

## Versions

### v1 — Minimum Viable Agent

Core agent that works on any Next.js project with basic tools and safety via git snapshots.

| Feature | Description |
|---|---|
| Single worker agent | One agent, one task at a time, no orchestrator |
| LLM integration | OpenAI-compatible API (OpenAI, NVIDIA, Anthropic, Ollama) |
| File operations | Read, write, edit, delete, list directory |
| Package management | Install and uninstall npm/pnpm packages |
| Git snapshots | Branch per task, commit tracking, diff, merge or discard |
| Approval flow | Show plan before executing, approve/deny/custom input at each step |
| CLI entry point | `nextjs-agent init`, `nextjs-agent run` |
| Pydantic models | Typed state and tool arguments |

### v2 — Context & Safety

Agent gets smarter about context and safer with user control.

| Feature | Description |
|---|---|
| Orchestrator-worker architecture | Planner breaks goals into tasks, worker executes atomically |
| Context compaction | Summarize long conversations to stay within token limits |
| Error recovery | Retry failed tools, adjust approach on failure |
| Dev server management | Start, stop, health check for `npm run dev` |
| Type checking | Run `tsc --noEmit`, report errors to agent |
| Linting | Run eslint, report issues to agent |
| Next.js route awareness | Understand App Router conventions (page.tsx, layout.tsx, route.ts) |
| Framework detection | Identify Next.js version, installed packages, config |

### v3 — Visual Preview

Agent can see what it builds. The x-factor.

| Feature | Description |
|---|---|
| Browser automation | Playwright-based headless Chromium |
| Page navigation | Navigate to any route in the running app |
| Click interactions | Click buttons, links, form elements |
| Screenshot capture | Visual state at any point |
| Console monitoring | Catch JS errors, hydration warnings |
| DOM inspection | Read accessible page structure |
| Visual diff | Before/after comparison of changes |
| Live preview panel | See the app running with agent's changes |

### v4 — Session & Polish

Production-ready experience.

| Feature | Description |
|---|---|
| Session handling | Save/resume conversations across restarts |
| Session list | View past sessions, pick one to continue |
| Auto-save | Don't lose work on crash or exit |
| Multi-task workflows | Agent handles complex multi-step requests |
| Streaming responses | Real-time output as agent thinks |
| Config management | Provider, model, preferences persisted |

## Tech Stack

| Component | Tech | Why |
|---|---|---|
| Language | Python | Rich ecosystem, fast iteration |
| LLM Client | OpenAI SDK | Works with OpenAI, NVIDIA, Anthropic, Ollama |
| Models | Pydantic | Validates LLM responses, typed tool arguments |
| Browser | Playwright | Screenshots, DOM access, console monitoring |
| Git | subprocess + git CLI | No extra dependency, battle-tested |
| CLI | click + rich | Interactive prompts, styled output |

## Project Structure

```
nextjs-agent/
├── pyproject.toml
├── README.md
├── .env                          # API keys (gitignored)
├── .nextjs-agent/
│   └── config.json               # Provider, model settings (gitignored)
├── nextjs_agent/
│   ├── __init__.py
│   ├── cli.py                    # CLI: init, run
│   ├── config.py                 # Config management
│   ├── agent/
│   │   └── worker.py
│   ├── tools/
│   │   ├── base.py               # Tool ABC
│   │   ├── registry.py
│   │   └── file-ops/
│   │       ├── ReadFileTool.py
│   │       ├── WriteFileTool.py
│   │       ├── EditFileTool.py
│   │       └── DeleteFileTool.py
│   ├── snapshots/
│   │   └── manager.py
│   └── models/
│       ├── state.py
│       ├── task_result.py
│       └── exceptions.py
```

## Setup

```bash
pip install nextjs-agent
nextjs-agent init
```

## Usage

```bash
cd ~/my-nextjs-app
nextjs-agent

>>> Add a navbar with dark mode toggle
```

---

## Development Progress

### Completed
- [x] Project setup (pyproject.toml, CLI, config)
- [x] CLI with rich UI (banner, provider table, masked API keys, model picker)
- [x] Config management (.env for keys, .nextjs-agent/config.json for settings)
- [x] Multi-provider support (OpenAI, NVIDIA, Anthropic, Ollama, Groq, etc.)
- [x] Dual API key support (main agent + worker agent, or same key for both)
- [x] Pydantic models (AgentState, TaskResult, ToolCall, FunctionCall)
- [x] Tool base class (ABC, abstract execute, resolve_project_path)
- [x] ReadFileTool (line-based reading, 1-indexed, start/end support)
- [x] EditFileTool (line-based edit, insert/replace/append, atomic writes, permission preservation)

### In Progress
- [ ] WriteFileTool
- [ ] DeleteFileTool
- [ ] ListDirTool

### Not Started
- [ ] Package tools (install, uninstall)
- [ ] Git snapshot manager
- [ ] LLM client
- [ ] Worker agent loop
- [ ] System prompt
- [ ] Approval flow
