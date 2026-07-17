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

Core agent that works on any Next.js project with basic tools and orchestration.

| Feature | Description |
|---|---|
| Orchestrator-worker architecture | Planner explores codebase, delegates writes to worker |
| Worker agent | Executes tasks with retry/backoff, error handling |
| LLM integration | OpenAI-compatible API (OpenAI, NVIDIA, Anthropic, Ollama) |
| File operations | Read, write, find & replace, delete, list directory, create directory |
| Code search | Cross-project grep with regex, context lines, file filters |
| Package management | Install and uninstall npm/pnpm/yarn/bun packages |
| CLI entry point | `nextjs-agent init`, `nextjs-agent run` |
| Pydantic models | Typed state, tool arguments, LLM responses |

### v2 — Context & Safety

Agent gets smarter about context and safer with user control.

| Feature | Description |
|---|---|
| Persistent memory | Remember decisions and context across tasks in a session |
| Context compaction | Summarize long conversations to stay within token limits |
| Context memory display | Show how much context has been filled |
| Git snapshots | Branch per task, commit tracking, diff, merge or discard |
| Approval flow | Show plan before executing, approve/deny/custom input |
| Error recovery | Retry failed tools, adjust approach on failure |
| Dev server management | Start, stop, health check for `npm run dev` |
| Type checking | Run `tsc --noEmit`, report errors to agent |
| Linting | Run eslint, report issues to agent |

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

### v4 — Session & Polish

Production-ready experience.

| Feature | Description |
|---|---|
| Session handling | Save/resume conversations across restarts |
| Session list | View past sessions, pick one to continue |
| Auto-save | Don't lose work on crash or exit |
| Multi-task workflows | Agent handles complex multi-step requests |
| Streaming responses | Real-time output as agent thinks |
| Web search | Tavily/Firecrawl integration for real-time knowledge |

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
├── .env                              # API keys (gitignored)
├── .nextjs-agent/
│   └── config.json                   # Provider, model settings (gitignored)
├── nextjs_agent/
│   ├── __init__.py
│   ├── cli.py                        # CLI: init, run
│   ├── config.py                     # Config management, provider detection
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator_agent.py      # ReACT loop, JSON response, delegation
│   │   │   ├── orchestrator_client.py     # OpenAI client for orchestrator
│   │   │   └── orchestrator_sys_prompt.py # Planner + delegator prompt
│   │   └── worker/
│   │       ├── __init__.py
│   │       ├── worker_agent.py            # Executor loop, tool execution
│   │       ├── worker_client.py           # OpenAI client for worker
│   │       └── worker_sys_prompt.py       # Tool-based execution prompt
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py                        # Tool ABC, resolve_project_path
│   │   ├── tools_registry.py              # create_tools, create_read_only_tools
│   │   ├── file_ops/
│   │   │   ├── ReadFileTool.py            # Line-based reading with line numbers
│   │   │   ├── WriteFileTool.py           # Create/overwrite files
│   │   │   ├── FindAndReplaceTool.py      # Exact text substitution
│   │   │   └── DeleteFileTool.py          # File deletion
│   │   ├── dir_ops/
│   │   │   ├── ListDirTool.py             # Recursive listing, depth control
│   │   │   └── CreateDirTool.py           # mkdir -p style
│   │   ├── search/
│   │   │   └── SearchCodeTool.py          # Cross-project grep, regex, context
│   │   └── package_tools/
│   │       ├── detect_manager.py          # Lock file detection
│   │       ├── AddPackageTool.py          # Install packages
│   │       └── RemovePackageTool.py       # Remove packages
│   └── models/
│       ├── __init__.py
│       ├── state.py                       # AgentState
│       ├── task.py                        # Task model (goal, context, relevant_files)
│       ├── task_result.py                 # TaskResult (success, summary, modified_files)
│       ├── orchestrator_response.py       # OrchestratorResponse (thought, action, tool_calls)
│       ├── worker_models.py               # FunctionCall, ToolCall, AssistantResponse
│       └── exceptions.py                  # All custom exceptions
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

#### Core Infrastructure
- [x] Project setup (pyproject.toml, dependencies, package structure)
- [x] CLI with rich UI (banner, provider table, masked API keys, model picker)
- [x] Config management (.env for keys, .nextjs-agent/config.json for settings)
- [x] Multi-provider support (OpenAI, NVIDIA, Anthropic, Ollama, Groq, etc.)
- [x] Dual API key support (orchestrator + worker agent, or same key for both)

#### Models
- [x] AgentState (task, messages, branch, status, modified_files, error)
- [x] Task (goal, context, relevant_files)
- [x] TaskResult (success, summary, modified_files, error)
- [x] OrchestratorResponse (thought, action, tool_calls, delegate_task, final_answer)
- [x] FunctionCall, ToolCall, AssistantResponse (worker models)
- [x] All custom exceptions (WorkerError, ToolExecutionError, etc.)

#### Tools
- [x] Tool base class (ABC, abstract execute, resolve_project_path)
- [x] ReadFileTool (line-based reading, 1-indexed, line numbers in output)
- [x] WriteFileTool (create new, overwrite existing, mode parameter)
- [x] FindAndReplaceTool (exact text substitution, replace_all)
- [x] DeleteFileTool (file deletion with error handling)
- [x] ListDirTool (recursive listing, depth control, ignore list)
- [x] CreateDirTool (mkdir -p style, idempotent)
- [x] SearchCodeTool (cross-project grep, regex, context lines, file filters, max_matches_per_file)
- [x] AddPackageTool (auto-detect npm/pnpm/yarn/bun)
- [x] RemovePackageTool (auto-detect manager, clean removal)
- [x] detect_manager utility (lock file detection)
- [x] Tool registry (create_tools, create_read_only_tools, get_tools_schema)

#### Agents
- [x] Worker agent loop (executor, LLM calls, tool execution, retry/backoff, error handling)
- [x] Worker system prompt (tool-based, concise, find_and_replace editing pattern)
- [x] Orchestrator agent (ReACT loop, JSON response, delegation to worker)
- [x] Orchestrator system prompt (planner + delegator, read-only tools)

### In Progress
- [ ] CLI `run` command (connect orchestrator → worker → user)

### Not Started
- [ ] Persistent memory (remember decisions across tasks)
- [ ] Context compaction (summarize long conversations)
- [ ] Context memory display (show token usage)
- [ ] Git snapshot manager (branch per task, commit, diff, merge, discard)
- [ ] Approval flow (show plan, approve/deny, view diff)

### Deferred (v2+)
- [ ] Web search tool (Tavily/Firecrawl integration)
- [ ] Dev server management
- [ ] Type checking / linting integration
- [ ] Browser automation (Playwright)
- [ ] Session handling
