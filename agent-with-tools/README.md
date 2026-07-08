# agent-with-tools

A two-tier AI agent system built for learning — orchestrator plans, worker executes using filesystem tools.

## Structure

```
agent/
├── orchestrator/          # High-level "manager" agent
│   ├── orchestrator_agent.py
│   ├── main_client.py     # OpenAI client (orchestrator)
│   └── sys_prompt.py
├── worker/                # "Doer" agent that uses tools
│   ├── worker_agent.py
│   ├── worker_client.py   # OpenAI client (worker)
│   ├── worker_model.py
│   └── sys_prompt.py
├── models/                # Data models & exceptions
│   ├── task.py
│   ├── task_result.py
│   └── exceptions.py
└── tools/                 # Filesystem tools the worker can use
    ├── base.py
    ├── tool_registery.py
    ├── file_operations/   # read_file, write_file, replace_in_file
    └── dir_operations/    # create_dir, list_dir_recursive
```

## How it works

1. You type a goal into the CLI (e.g. "create an index.html with a blue button")
2. **Orchestrator** LLM receives it, plans, and delegates subtasks to the worker
3. **Worker** LLM receives each task and calls filesystem tools to complete it
4. Results flow back up — the orchestrator reflects and may delegate again
5. Conversation history auto-compacts when token count exceeds ~100K

Both agents talk to **NVIDIA NIM** (`integrate.api.nvidia.com/v1`) via the OpenAI SDK.

## Setup

```bash
uv sync
```

Create a `.env` file:

```env
MAIN_NVIDIA_API_KEY=your_key_here
NVIDIA_API_KEY=your_key_here
```

## Run

```bash
uv run python agent/orchestrator/orchestrator_agent.py
```

Type a goal at the `>>>` prompt. Type `quit` to exit.

## Dependencies

`openai`, `pydantic`, `python-dotenv`, `tiktoken` (Python 3.11+)
