import os
from pathlib import Path
from pydantic import BaseModel, Field

from agent.tools.base import Tool

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".next",
    "dist",
    "build",
}


class ListDirRecursiveArgs(BaseModel):
    path: str = Field(
        default=".",
        min_length=1,
        description="Directory to recursively scan.",
    )


class ListDirRecursiveTool(Tool):
    name = "list_dir_recursive"
    description = (
        "Recursively list all files and directories under a directory. "
        "Use this to understand the overall project structure before reading or modifying files. "
        "Common dependency directories such as .git, .venv, node_modules, __pycache__, "
        ".next, dist, and build are skipped automatically."
    )

    args_schema = ListDirRecursiveArgs

    async def execute(self, args: ListDirRecursiveArgs):
        dir_path = self.resolve_project_path(args.path)
        project_root = Path.cwd()

        if not dir_path.exists():
            raise FileNotFoundError(f"{args.path} does not exist.")

        if not dir_path.is_dir():
            raise ValueError(f"{args.path} is not a directory.")

        directories: list[str] = []
        files: list[str] = []

        for root, dirs, filenames in os.walk(dir_path, topdown=True):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]

            rel_root = Path(root).relative_to(project_root)

            for d in dirs:
                directories.append(str(rel_root / d))
            for f in filenames:
                files.append(str(rel_root / f))

        return {
            "path": args.path,
            "directories": sorted(directories),
            "files": sorted(files),
            "modified_files": [],
        }
