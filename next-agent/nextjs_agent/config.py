import json
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

PACKAGE_DIR = Path(__file__).parent.parent  # next-agent/


def _find_project_root() -> Path:
    """Find the Next.js project root by looking for package.json with 'next' dependency."""
    cwd = Path.cwd()

    # Check cwd first
    pkg = cwd / "package.json"
    if pkg.exists() and "next" in pkg.read_text():
        return cwd

    # Check parent (for when running from next-agent/ subdirectory)
    pkg = cwd.parent / "package.json"
    if pkg.exists() and "next" in pkg.read_text():
        return cwd.parent

    # Fallback to cwd
    return cwd


PROJECT_ROOT = _find_project_root()
CONFIG_DIR = PACKAGE_DIR / ".nextjs-agent"
CONFIG_FILE = CONFIG_DIR / "config.json"
SESSIONS_DIR = CONFIG_DIR / "sessions"

PROVIDERS = {
    "anthropic": {"base_url": "https://api.anthropic.com/v1"},
    "cerebras": {"base_url": "https://api.cerebras.ai/v1"},
    "deepseek": {"base_url": "https://api.deepseek.com"},
    "groq": {"base_url": "https://api.groq.com/openai/v1"},
    "mistral": {"base_url": "https://api.mistral.ai/v1"},
    "nvidia": {"base_url": "https://integrate.api.nvidia.com/v1"},
    "ollama": {"base_url": "http://localhost:11434/v1"},
    "openai": {"base_url": "https://api.openai.com/v1"},
    "openrouter": {"base_url": "https://openrouter.ai/api/v1"},
}

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-5",
    "cerebras": "gpt-oss-120b",
    "deepseek": "deepseek-v4-flash",
    "groq": "openai/gpt-oss-120b",
    "mistral": "mistral-small-2603",
    "nvidia": "openai/gpt-oss-120b",
    "ollama": "llama3.1",
    "openai": "gpt-4o",
    "openrouter": "tencent/hy3:free",
}


@dataclass
class Config:
    provider: str = "openai"
    model: str = ""
    same_key: bool = True

    def get_base_url(self) -> str:
        return PROVIDERS[self.provider]["base_url"]

    def get_model(self) -> str:
        return self.model or DEFAULT_MODELS[self.provider]

    def get_worker_key(self) -> str:
        return os.getenv("WORKER_AGENT_API_KEY", "")

    def get_main_key(self) -> str:
        if self.same_key:
            return self.get_worker_key()
        return os.getenv("MAIN_AGENT_API_KEY", "")

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "provider": self.provider,
            "model": self.model,
            "same_key": self.same_key,
        }
        CONFIG_FILE.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls) -> "Config":
        if not CONFIG_FILE.exists():
            return cls()
        try:
            data = json.loads(CONFIG_FILE.read_text())
            return cls(
                provider=data.get("provider", "openai"),
                model=data.get("model", "openai/gpt-oss-120b"),
                same_key=data.get("same_key", True),
            )
        except (json.JSONDecodeError, KeyError):
            return cls()

    def is_configured(self) -> bool:
        if self.provider == "ollama":
            return True
        worker_key = self.get_worker_key()
        if self.same_key:
            return bool(worker_key)
        return bool(worker_key and self.get_main_key())
