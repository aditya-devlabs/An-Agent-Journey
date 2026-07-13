from pathlib import Path
def detect_manager(project_root: Path) -> str:
    if (project_root / "pnpm-lock.yaml").exists(): return "pnpm"
    if (project_root / "yarn.lock").exists(): return "yarn"
    if (project_root / "bun.lockb").exists(): return "bun"
    return "npm"