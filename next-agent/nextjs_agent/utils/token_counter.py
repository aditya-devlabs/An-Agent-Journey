import tiktoken
from rich.console import Console

console = Console()

MODEL_TOKEN_LIMITS = {
    "openai": 128000,
    "anthropic": 200000,
    "ollama": 8192,
    "groq": 8192,
    "deepseek": 64000,
    "mistral": 32000,
    "nvidia": 8192,
    "cerebras": 8192,
    "openrouter": 8192,
}


def count_tokens(text: str, model: str = "gpt-4") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def count_history_tokens(history: list[str], model: str = "gpt-4") -> int:
    return sum(count_tokens(msg, model) for msg in history)


def get_model_limit(provider: str) -> int:
    return MODEL_TOKEN_LIMITS.get(provider, 8192)


def print_context_usage(history: list[str], provider: str, model: str):
    tokens = count_history_tokens(history, model)
    max_tokens = get_model_limit(provider)
    percentage = (tokens / max_tokens) * 100

    if percentage < 60:
        color = "green"
    elif percentage < 80:
        color = "yellow"
    else:
        color = "red"

    console.print(
        f"  [dim][{color}]{percentage:.0f}% context used ({tokens:,}/{max_tokens:,} tokens)[/{color}][/dim]"
    )
