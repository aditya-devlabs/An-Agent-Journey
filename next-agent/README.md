# nextjs-agent

Site Entirely created by this agent harness : [Coffee Site](https://origin-roast-coffee-site.vercel.app/)

A toy project to learn how agent harnesses work. Orchestrator-worker architecture for Next.js projects — you describe what you want, the agent plans and executes it.

Built to understand how AI coding agents work under the hood. Feel free to try it out if you're curious.

## How It Works

```
You: "Create a dark mode toggle"

Orchestrator (planner)
  → Reads project tree
  → Creates task: "Create DarkModeToggle component and integrate into layout"

Worker (executor)
  → Reads frontend-design skill
  → Explores existing layout
  → Creates component, updates files
  → Returns summary

Orchestrator
  → Checks progress
  → Returns done or creates next task
```

The orchestrator has no tools — it only plans. The worker has 11 tools and does all the actual work. Each task is self-contained: the worker reads skills, explores files, and completes the deliverable in one go.

## Features

| Feature             | What it does                                                        |
| ------------------- | ------------------------------------------------------------------- |
| Orchestrator-worker | Stateless planner + executor with tools                             |
| 11 tools            | File ops, directory ops, code search, package management, skills    |
| 4 skills            | frontend-design, tailwind-css, vercel-react-best-practices, caveman |
| Sessions            | Save, resume, list, delete conversations                            |
| Context compaction  | Auto-summarizes when context hits 80% of token limit                |
| 9 providers         | OpenAI, Anthropic, Ollama, Groq, OpenRouter, etc.                   |
| Dual API keys       | Separate keys for orchestrator and worker (or same key for both)    |

## Setup

### 1. Go inside your Next.js repo

```bash
cd ~/my-nextjs-app
```

### 2. Clone

```bash
git clone https://github.com/aditya-devlabs/An-Agent-Journey/tree/main/next-agent
cd nextjs-agent
```

### 3. Create virtual environment

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**

```bash
python3 -m venv .venv
.venv\Scripts\activate
```



### 4. Install

**Using pip:**

```bash
pip install -e .
```

**Using uv:**

```bash
uv sync
```

### 5. Configure

```bash
nextjs_agent init
```

This asks for your provider, model, and API key. Saves config to `.nextjs-agent/config.json` and keys to `.env`.

## Usage

### Start the agent

```bash
cd ~/my-nextjs-app
nextjs_agent run
```

### Interact

```
You: Create a contact page with a form and map

Orchestrator (thinking...)
  Thought: User wants a contact page...
  Task: Create app/contact/page.tsx with form and map...

Worker (executing...)
  ✓ Created app/contact/page.tsx

Done: Contact page created.
```

### Exit

Type `quit`, `exit`, `q`, or press `Ctrl+C`.

### Resume a session

```bash
nextjs_agent run --session <session-id>
```

## CLI Commands

| Command                             | Description                         |
| ----------------------------------- | ----------------------------------- |
| `nextjs_agent init`                 | Configure provider, model, API keys |
| `nextjs_agent run`                  | Start the agent                     |
| `nextjs_agent run --new`            | Start with fresh session            |
| `nextjs_agent run --session <id>`   | Resume a session                    |
| `nextjs_agent sessions list`        | List all sessions                   |
| `nextjs_agent sessions show <id>`   | Show session messages               |
| `nextjs_agent sessions delete <id>` | Delete a session                    |
| `nextjs_agent uninstall`            | Remove next-agent from your project |

## Tools

### File Operations

| Tool                                    | Description                                     |
| --------------------------------------- | ----------------------------------------------- |
| `read_file(path, start?, end?)`         | Read files with line numbers                    |
| `write_file(path, content, mode)`       | Create (`"write"`) or overwrite (`"overwrite"`) |
| `find_and_replace(path, find, replace)` | Exact text substitution                         |
| `delete_file(path)`                     | Delete a file                                   |

### Directory Operations

| Tool                      | Description                 |
| ------------------------- | --------------------------- |
| `list_dir(path?, depth?)` | List directory recursively  |
| `create_dir(path)`        | Create directory (mkdir -p) |

### Search

| Tool                                            | Description                      |
| ----------------------------------------------- | -------------------------------- |
| `search_code(pattern, path?, include?, regex?)` | Multi-threaded grep with context |

### Package Management

| Tool                      | Description                        |
| ------------------------- | ---------------------------------- |
| `add_package(package)`    | Install npm/pnpm/yarn/bun packages |
| `remove_package(package)` | Remove packages                    |

### Skills

| Tool                     | Description                 |
| ------------------------ | --------------------------- |
| `list_skills()`          | List available skills       |
| `read_skill(skill_name)` | Read a skill's full content |

## Skills

The worker can read these for guidance:

| Skill                         | What it covers                                                 |
| ----------------------------- | -------------------------------------------------------------- |
| `frontend-design`             | Design guidance — typography, palette, layout, visual identity |
| `tailwind-css`                | Tailwind CSS utility classes reference                         |
| `vercel-react-best-practices` | React/Next.js performance rules (70+ rules)                    |
| `caveman`                     | Token-efficient communication — cuts output tokens 65%         |

## Providers

| Provider   | Default Model       | Notes          |
| ---------- | ------------------- | -------------- |
| openai     | gpt-4o              | Paid           |
| anthropic  | claude-sonnet-5     | Paid           |
| openrouter | tencent/hy3:free    | Free tier      |
| ollama     | llama3.1            | Local          |
| groq       | openai/gpt-oss-120b | Fast inference |
| deepseek   | deepseek-v4-flash   | Paid           |
| mistral    | mistral-small-2603  | Paid           |
| cerebras   | gpt-oss-120b        | Fast inference |
| nvidia     | openai/gpt-oss-120b | Paid           |

## Project Structure

```
next-agent/
├── .agents/skills/              # Agent skills
├── .nextjs-agent/               # Config + sessions (gitignored)
├── nextjs_agent/
│   ├── cli.py                   # CLI commands
│   ├── config.py                # Provider/model config
│   ├── runner.py                # Orchestrator-worker loop
│   ├── sessions.py              # Session management
│   ├── agents/
│   │   ├── orchestrator/        # Planner (no tools)
│   │   └── worker/              # Executor (with tools)
│   ├── tools/                   # 11 tools
│   │   ├── file_ops/            # read, write, replace, delete
│   │   ├── dir_ops/             # list, create
│   │   ├── search/              # grep
│   │   ├── package_tools/       # add, remove
│   │   └── skill_tools/         # list, read
│   ├── models/                  # Pydantic models
│   └── utils/                   # Token counting, context compaction
└── pyproject.toml
```

## Removal

To completely remove next-agent from your project:

```bash
cd ~/my-nextjs-app
nextjs_agent uninstall
```

Or manually:

```bash
rm -rf next-agent/
```

## Tech Stack

| Component  | Tech         |
| ---------- | ------------ |
| Language   | Python 3.11+ |
| LLM Client | OpenAI SDK   |
| Models     | Pydantic v2  |
| CLI        | click + rich |
| Tokens     | tiktoken     |

---

A learning project to understand how AI agent harnesses work. Not a production tool — just exploration.
