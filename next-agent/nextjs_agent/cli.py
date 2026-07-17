import asyncio
import shutil
import subprocess
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box
from pathlib import Path

from nextjs_agent.config import Config, PROVIDERS, DEFAULT_MODELS, PROJECT_ROOT, PACKAGE_DIR, CONFIG_DIR

console = Console()

BANNER = """
 ██╗   ██╗██████╗  ██████╗ ███████╗██╗███╗   ██╗
 ██║   ██║██╔══██╗██╔═══██╗██╔════╝██║████╗  ██║
 ██║   ██║██████╔╝██║   ██║███████╗██║██╔██╗ ██║
 ╚██╗ ██╔╝██╔══██╗██║   ██║╚════██║██║██║╚██╗██║
  ╚████╔╝ ██║  ██║╚██████╔╝███████║██║██║ ╚████║
   ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝
"""


def show_banner():
    console.print(Text(BANNER, style="bold cyan"), justify="center")
    console.print(
        Panel(
            "[bold]AI Agent Harness for Next.js Projects[/bold]",
            style="cyan",
            box=box.ROUNDED,
        ),
        justify="center",
    )
    console.print()


def mask_key(key: str) -> str:
    if not key:
        return "(not set)"
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


def pick_provider(config: Config) -> str:
    console.print("[bold]Step 1:[/bold] Choose your AI provider\n")

    table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold cyan")
    table.add_column("#", style="bold", width=3)
    table.add_column("Provider", style="bold")
    table.add_column("Default Model", style="dim")
    table.add_column("Base URL", style="dim")

    providers = list(PROVIDERS.keys())
    for i, name in enumerate(providers, 1):
        is_current = " ← current" if name == config.provider else ""
        table.add_row(
            str(i),
            f"{name}{is_current}",
            DEFAULT_MODELS[name],
            PROVIDERS[name]["base_url"],
        )

    console.print(table)
    console.print()

    choice = Prompt.ask(
        "Select provider",
        choices=[str(i) for i in range(1, len(providers) + 1)],
        default="1",
    )
    return providers[int(choice) - 1]


def pick_model(config: Config, provider: str) -> str:
    console.print(f"\n[bold]Step 2:[/bold] Choose model for [cyan]{provider}[/cyan]\n")

    default_model = DEFAULT_MODELS[provider]

    table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold cyan")
    table.add_column("#", style="bold", width=3)
    table.add_column("Model")
    table.add_column("Note", style="dim")

    table.add_row("1", default_model, "← recommended")
    table.add_row("2", "Custom", "enter any model name")

    console.print(table)
    console.print()

    choice = Prompt.ask("Select option", choices=["1", "2"], default="1")

    if choice == "1":
        console.print(f"  Using [green]{default_model}[/green]")
        return default_model

    custom = Prompt.ask("  Enter model name")
    if not custom.strip():
        console.print("[red]Model name cannot be empty[/red]")
        return pick_model(config, provider)

    return custom.strip()


def setup_keys(config: Config, provider: str) -> bool:
    console.print(f"\n[bold]Step 3:[/bold] API keys\n")

    if provider == "ollama":
        console.print("  [dim]Ollama runs locally — no API key needed[/dim]\n")
        return True

    same = Confirm.ask(
        "  Use the same API key for both main and worker agent?",
        default=True,
    )

    env_file = PACKAGE_DIR / ".env"
    lines = env_file.read_text().splitlines() if env_file.exists() else []

    def update_env(key: str, value: str):
        nonlocal lines
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f'{key}="{value}"'
                found = True
                break
        if not found:
            lines.append(f'{key}="{value}"')

    if same:
        console.print(
            f"\n  [dim]This key will be used for both main and worker agent[/dim]"
        )
        key = Prompt.ask(
            "  API key"
        )  # password = True, will paste the api key but will not show the key on terminal
        if not key.strip():
            console.print("[red]API key cannot be empty[/red]")
            return setup_keys(config, provider)
        update_env("WORKER_AGENT_API_KEY", key.strip())
        update_env("MAIN_AGENT_API_KEY", key.strip())
        config.same_key = True
    else:
        console.print(f"\n  [dim]Provide separate keys for each agent[/dim]\n")

        console.print("  [bold]Main agent[/bold] (orchestrator — plans tasks)")
        main_key = Prompt.ask("  API key", password=True)
        if not main_key.strip():
            console.print("[red]API key cannot be empty[/red]")
            return setup_keys(config, provider)

        console.print("\n  [bold]Worker agent[/bold] (executes tasks)")
        worker_key = Prompt.ask("  API key", password=True)
        if not worker_key.strip():
            console.print("[red]API key cannot be empty[/red]")
            return setup_keys(config, provider)

        update_env("MAIN_AGENT_API_KEY", main_key.strip())
        update_env("WORKER_AGENT_API_KEY", worker_key.strip())
        config.same_key = False

    env_file.write_text("\n".join(lines) + "\n")
    return True


@click.group()
def cli():
    """nextjs-agent: An AI agent harness for Next.js projects."""
    pass


@cli.command()
def init():
    """Setup API key, provider, and model."""
    show_banner()

    config = Config.load()

    provider = pick_provider(config)
    model = pick_model(config, provider)
    setup_keys(config, provider)

    config.provider = provider
    config.model = model
    config.save()

    env_file = PACKAGE_DIR / ".env"
    env_lines = env_file.read_text().splitlines() if env_file.exists() else []
    worker_key = ""
    main_key = ""
    for line in env_lines:
        if line.startswith("WORKER_AGENT_API_KEY="):
            worker_key = line.split("=", 1)[1].strip('"')
        elif line.startswith("MAIN_AGENT_API_KEY="):
            main_key = line.split("=", 1)[1].strip('"')

    console.print()
    console.print(
        Panel(
            f"[bold green]Setup complete![/bold green]\n\n"
            f"  Provider  : [cyan]{provider}[/cyan]\n"
            f"  Model     : [cyan]{model}[/cyan]\n"
            f"  Main key  : [dim]{mask_key(main_key)}[/dim]\n"
            f"  Worker key: [dim]{mask_key(worker_key)}[/dim]\n"
            f"  Same key  : [dim]{'yes' if config.same_key else 'no'}[/dim]\n\n"
            f"  Config    : [dim].nextjs-agent/config.json[/dim]\n"
            f"  Keys      : [dim].env[/dim]",
            title="[bold]Configuration[/bold]",
            style="green",
            box=box.ROUNDED,
        )
    )

    console.print("\n[bold]Next steps:[/bold]")
    console.print("  nextjs-agent run\n")


@cli.command()
@click.option("--new", is_flag=True, help="Start a new session")
@click.option("--session", "session_id", default=None, help="Resume a specific session by ID")
def run(new: bool, session_id: str | None):
    """Start the agent in the current directory."""
    show_banner()

    config = Config.load()

    if not config.is_configured():
        console.print(
            "[red]Not configured. Run [bold]nextjs-agent init[/bold] first.[/red]"
        )
        return

    from nextjs_agent.sessions import list_sessions

    if not new and not session_id:
        recent = list_sessions()
        if recent:
            console.print("\n[bold]Recent sessions:[/bold]\n")
            table = Table(box=box.SIMPLE_HEAVY, show_header=False)
            table.add_column("#", style="bold", width=3)
            table.add_column("ID", style="dim")
            table.add_column("Messages", style="dim")
            table.add_column("Last updated", style="dim")
            for i, s in enumerate(recent[:5], 1):
                table.add_row(
                    str(i),
                    s["id"][:8] + "...",
                    str(s["message_count"]),
                    s["updated_at"][:19].replace("T", " "),
                )
            table.add_row("n", "[dim]New session[/dim]", "", "")
            console.print(table)
            console.print()

            choice = Prompt.ask(
                "Select session",
                default="n",
            )
            if choice.lower() != "n" and choice.isdigit() and 1 <= int(choice) <= len(recent):
                session_id = recent[int(choice) - 1]["id"]

    console.print(
        Panel(
            f"  Provider : [cyan]{config.provider}[/cyan]\n"
            f"  Model    : [cyan]{config.get_model()}[/cyan]\n"
            f"  Project  : [cyan]{PROJECT_ROOT}[/cyan]"
            + (f"\n  Session  : [dim]{session_id[:8]}...[/dim]" if session_id else ""),
            title="[bold]Agent Ready[/bold]",
            style="cyan",
            box=box.ROUNDED,
        )
    )
    console.print()

    from nextjs_agent.runner import run_agent

    asyncio.run(run_agent(config, session_id))

@cli.group()
def sessions():
    """List, show, and manage sessions."""
    pass


@sessions.command("list")
def sessions_list():
    """Show all saved sessions."""
    from nextjs_agent.sessions import list_sessions

    all_sessions = list_sessions()
    if not all_sessions:
        console.print("[yellow]No sessions found.[/yellow]")
        return

    table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold cyan")
    table.add_column("Session ID", style="bold")
    table.add_column("Messages", style="dim")
    table.add_column("Created", style="dim")
    table.add_column("Last updated", style="dim")

    for s in all_sessions:
        table.add_row(
            s["id"][:8],
            str(s["message_count"]),
            s["created_at"][:19].replace("T", " "),
            s["updated_at"][:19].replace("T", " "),
        )

    console.print(table)
    console.print(f"  [dim]Full IDs (copy-paste):[/dim]")
    for s in all_sessions:
        console.print(f"    {s['id']}")
    console.print(f"\n  [dim]{len(all_sessions)} session(s)[/dim]")


@sessions.command("show")
@click.argument("session_id")
def sessions_show(session_id: str):
    """Show messages in a session."""
    from nextjs_agent.sessions import load_session

    session = load_session(session_id)
    if not session:
        console.print(f"[red]Session '{session_id}' not found.[/red]")
        return

    for msg in session.get("messages", []):
        role = msg.get("role", "unknown")
        content = (msg.get("content") or "")[:500]
        if role == "system":
            continue
        color = {"user": "green", "assistant": "cyan"}.get(role, "white")
        console.print(f"  [[{color}]{role}[/{color}]] {content}")


@sessions.command("delete")
@click.argument("session_id")
def sessions_delete(session_id: str):
    """Delete a session."""
    from nextjs_agent.sessions import delete_session

    if Confirm.ask(f"  Delete session '{session_id[:8]}...'?", default=False):
        if delete_session(session_id):
            console.print("[green]Deleted.[/green]")
        else:
            console.print(f"[red]Session '{session_id}' not found.[/red]")


@cli.command()
def uninstall():
    """Remove nextjs-agent configuration and session files."""
    show_banner()

    removed = []

    if CONFIG_DIR.exists() or (PACKAGE_DIR / ".env").exists():
        console.print(
            Panel(
                "This will remove:\n"
                f"  [red]• {CONFIG_DIR}[/red]  (config, sessions)\n"
                f"  [red]• {PACKAGE_DIR / '.env'}[/red]  (API keys)\n\n"
                "[dim]Your project files will not be affected.[/dim]",
                title="[bold red]Remove Configuration[/bold red]",
                style="red",
                box=box.ROUNDED,
            )
        )

        if Confirm.ask("\n  Remove configuration?", default=False):
            if CONFIG_DIR.exists():
                shutil.rmtree(CONFIG_DIR)
                removed.append(str(CONFIG_DIR))

            env_file = PACKAGE_DIR / ".env"
            if env_file.exists():
                env_file.unlink()
                removed.append(str(env_file))

    if Confirm.ask("\n  Uninstall pip package?", default=False):
        result = subprocess.run(
            ["pip", "uninstall", "nextjs-agent", "-y"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            removed.append("pip package: nextjs-agent")
            console.print(f"  [dim]{result.stdout.strip()}[/dim]")
        else:
            console.print(f"  [red]Failed: {result.stderr.strip()}[/red]")
            return

    if not removed:
        console.print("[yellow]Nothing to remove.[/yellow]")
        return

    console.print()
    console.print(
        Panel(
            "\n".join(f"  [red]✗[/red] {path}" for path in removed),
            title="[bold green]Removed[/bold green]",
            style="green",
            box=box.ROUNDED,
        )
    )
    console.print("\n[bold green]Done.[/bold green]")


if __name__ == "__main__":
    cli()
