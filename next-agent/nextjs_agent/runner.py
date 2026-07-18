import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from pathlib import Path

from nextjs_agent.config import Config, PROJECT_ROOT
from nextjs_agent.agents.orchestrator.orchestrator_agent import call_orchestrator
from nextjs_agent.agents.orchestrator.orchestrator_client import orchestrator_client
from nextjs_agent.agents.worker.worker_agent import WorkerAgent
from nextjs_agent.agents.worker.worker_client import worker_client
from nextjs_agent.tools.tools_registry import create_tools
from nextjs_agent.tools.dir_ops.ListDirTool import ListDirTool, ListDirToolArgs
from nextjs_agent.models.task import Task
from nextjs_agent.sessions import create_session, save_session, load_session
from nextjs_agent.utils.context_compactor import compact_history
from nextjs_agent.utils.token_counter import print_context_usage

console = Console()

MAX_ORCHESTRATOR_CALLS = 10


async def get_tree_string(root: Path) -> str:
    tool = ListDirTool(root)
    result = await tool.execute(ListDirToolArgs(path=".", depth=3))

    if not result["success"]:
        return "Could not read project structure"

    all_paths = result["directories"] + result["files"]
    all_paths.sort()

    return "\n".join(all_paths)


async def run_agent(config: Config, session_id: str | None):
    console.print("\n[bold cyan]Starting agent...[/bold cyan]\n")

    fresh_tree = await get_tree_string(PROJECT_ROOT)
    worker_context: list[str] = []
    orchestrator_history: list[str] = []

    tools = create_tools(PROJECT_ROOT)
    worker = WorkerAgent(
        llm_client=worker_client,
        tool_registry=tools,
        config=config,
    )

    session = create_session()
    if session_id:
        existing = load_session(session_id)
        if existing:
            session = existing
            console.print(f"[dim]Resumed session {session_id[:8]}...[/dim]\n")

    while True:
        try:
            user_prompt = Prompt.ask("[bold green]You[/bold green]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Exiting...[/dim]")
            break

        if user_prompt.strip().lower() in ("quit", "exit", "q"):
            break

        if not user_prompt.strip():
            console.print("[dim]Enter a task, or 'quit' to exit.[/dim]")
            continue

        orchestrator_history.append(user_prompt)
        session["messages"].append({"role": "user", "content": user_prompt})

        orchestrator_history = await compact_history(
            orchestrator_history,
            orchestrator_client,
            config,
        )

        print_context_usage(orchestrator_history, config.provider, config.get_model())
        console.print()

        has_replanned = False
        has_retried_empty = False
        has_completed = False
        worker_context.clear()

        for i in range(MAX_ORCHESTRATOR_CALLS):
            if has_completed or (orchestrator_history and orchestrator_history[-1].startswith("Done:")):
                break

            console.print(f"[bold cyan]Orchestrator[/bold cyan] (thinking...)")

            response = await call_orchestrator(
                client=orchestrator_client,
                config=config,
                project_tree=fresh_tree,
                history=orchestrator_history,
            )

            console.print(f"  [dim]Thought: {response.thought}[/dim]")

            if response.done:
                console.print(
                    f"\n[bold green]Done:[/bold green] {response.reason}\n"
                )
                orchestrator_history.append(f"Done: {response.reason}")
                has_completed = True
                break

            task = response.task
            if task is None:
                if has_retried_empty:
                    console.print("[red]Task empty twice. Stopping.[/red]\n")
                    break
                has_retried_empty = True
                orchestrator_history.append(
                    "Previous loop: task was empty. This should not happen. Provide a valid task."
                )
                console.print("[yellow]Empty task. Retrying...[/yellow]\n")
                continue

            has_retried_empty = False
            console.print(f"  [bold]Task: {task.goal}[/bold]")
            if task.context:
                if len(task.context) > 100:
                    console.print(f"  [dim]Context: {task.context[:100]}...[/dim]")
                else:
                    console.print(f"  [dim]Context: {task.context}[/dim]")
            console.print()

            console.print(f"[bold cyan]Worker[/bold cyan] (executing...)")
            result = await worker.run(
                task=task,
                previous_context=worker_context,
                project_tree=fresh_tree,
            )

            if result.success:
                summary = result.summary or "Completed"
                worker_context.append(summary)
                orchestrator_history.append(f"Success: {summary}")
                console.print(f"  [green]✓[/green] {summary}")
            else:
                error = result.error or "Unknown error"
                orchestrator_history.append(f"Failed: {error}")
                console.print(f"  [red]✗[/red] {error}")

                if has_replanned:
                    console.print("\n[red]Failed twice. Stopping.[/red]\n")
                    break
                has_replanned = True

            if result.modified_files:
                console.print(
                    f"  [dim]Modified: {', '.join(result.modified_files)}[/dim]"
                )
                fresh_tree = await get_tree_string(PROJECT_ROOT)

            console.print()

        else:
            console.print("[yellow]Reached maximum orchestrator calls.[/yellow]\n")

        session["messages"].append(
            {
                "role": "assistant",
                "content": "\n".join(orchestrator_history),
            }
        )
        save_session(session)

    save_session(session)

    console.print(
        Panel(
            f"  Session: [dim]{session['id'][:8]}...[/dim]\n"
            f"  Messages: [dim]{len(session['messages'])}[/dim]",
            title="[bold]Session Saved[/bold]",
            style="cyan",
        )
    )
