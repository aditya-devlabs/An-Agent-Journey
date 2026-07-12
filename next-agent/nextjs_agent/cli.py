import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box
from pathlib import Path

from nextjs_agent.config import Config, PROVIDERS, DEFAULT_MODELS, PROJECT_ROOT

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

    env_file = PROJECT_ROOT / ".env"
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

    env_file = PROJECT_ROOT / ".env"
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
def run():
    """Start the agent in the current directory."""
    show_banner()

    config = Config.load()

    if not config.is_configured():
        console.print(
            "[red]Not configured. Run [bold]nextjs-agent init[/bold] first.[/red]"
        )
        return

    console.print(
        Panel(
            f"  Provider : [cyan]{config.provider}[/cyan]\n"
            f"  Model    : [cyan]{config.get_model()}[/cyan]\n"
            f"  Project  : [cyan]{PROJECT_ROOT}[/cyan]",
            title="[bold]Agent Ready[/bold]",
            style="cyan",
            box=box.ROUNDED,
        )
    )
    console.print()

    from nextjs_agent.agent.worker import run_worker

    run_worker(config)


if __name__ == "__main__":
    cli()
