from nextjs_agent.models.exceptions import ListDirToolError
from pathlib import Path
import os
from nextjs_agent.tools.base import TOOL
from pydantic import BaseModel, Field

ignored_files = {
    ".next",
    "node_modules",
    "__pycache__",
    ".git",
    ".venv",
    "dist",
    "build",
    ".nextjs-agent",
}


class ListDirToolArgs(BaseModel):
    path: str = "."  # will always start from the root of the project
    depth: int | None = None
    include_ignored: bool = False


class ListDirTool(TOOL):
    name = "list_dir"
    description = "Lists down all the subfolders and files from the root project."

    args_schema = ListDirToolArgs

    async def execute(self, args: ListDirToolArgs):

        dir_path = self.resolve_project_path(args.path).resolve()

        max_depth = args.depth
        all_files = []
        all_dirs = []

        try:
            for root, dirs, files in os.walk(dir_path, topdown=True):
                if not args.include_ignored:
                    dirs[:] = [d for d in dirs if d not in ignored_files]
                for f in files:
                    all_files.append(os.path.relpath(os.path.join(root, f), dir_path))
                for d in dirs:
                    all_dirs.append(os.path.relpath(os.path.join(root, d), dir_path))

                current_depth = Path(root).relative_to(dir_path).parts

                if max_depth is not None and len(current_depth) >= max_depth:
                    dirs.clear()


            return {
                    "success": True,
                    "summary": f"Walked down the project directory with the depth : {args.depth}",
                    "directories": all_dirs,
                    "files": all_files

                }

        except Exception as e:
            raise ListDirToolError(f"Error while traversing the directory. Error occurred: {e}")