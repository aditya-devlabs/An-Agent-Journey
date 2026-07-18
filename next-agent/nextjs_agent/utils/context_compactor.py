import asyncio
from openai import OpenAI
from rich.console import Console
from nextjs_agent.config import Config
from nextjs_agent.utils.token_counter import count_history_tokens, get_model_limit

console = Console()

COMPACT_TRIGGER_RATIO = 0.8
KEEP_RECENT = 5


async def compact_history(
    history: list[str],
    client: OpenAI,
    config: Config,
) -> list[str]:
    if len(history) <= KEEP_RECENT:
        return history

    tokens = count_history_tokens(history, config.get_model())
    max_tokens = get_model_limit(config.provider)
    threshold = max_tokens * COMPACT_TRIGGER_RATIO

    if tokens < threshold:
        return history

    console.print(
        f"  [dim][yellow]Compacting context ({tokens:,} tokens)...[/yellow][/dim]"
    )

    old_messages = history[:-KEEP_RECENT]
    recent_messages = history[-KEEP_RECENT:]

    summary = await _summarize(old_messages, client, config)

    compacted = [f"Previous context summary:\n{summary}"] + recent_messages

    new_tokens = count_history_tokens(compacted, config.get_model())
    console.print(
        f"  [dim][green]Compacted: {tokens:,} → {new_tokens:,} tokens[/green][/dim]"
    )

    return compacted


async def _summarize(
    messages: list[str],
    client: OpenAI,
    config: Config,
) -> str:
    numbered = "\n".join(f"{i+1}. {msg}" for i, msg in enumerate(messages))

    prompt = f"""Summarize this conversation history concisely.
Focus on: what was requested, what was done, key decisions made, current progress.

History:
{numbered}

Provide a brief summary (2-3 paragraphs max):"""

    response = await asyncio.to_thread(
        client.chat.completions.create,
        messages=[{"role": "user", "content": prompt}],
        model=config.get_model(),
    )

    return response.choices[0].message.content or "No summary generated."
