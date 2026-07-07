from pathlib import Path
from pydantic import BaseModel, Field
from agent.tools.base import Tool


class ListDirArgs(BaseModel):
    path: str = Field(default=".", min_length=1)  # calls the project root by default


class ListDirTool(Tool):
    name = "list_dir"
    description = "List the immediate files and subdirectories inside a directory. Use '.' for the root directory. "

    args_schema = ListDirArgs

    async def execute(self, args: ListDirArgs):

        dir_path = self.resolve_project_path(args.path)

        if not dir_path.exists():
            raise FileNotFoundError(f"{args.path} does not exist.")

        if not dir_path.is_dir():
            raise ValueError(f"{args.path} is not a directory.")

        directories = []
        files = []

        for item in dir_path.iterdir():
            if item.is_dir():
                directories.append(item.name)
            elif item.is_file():
                files.append(item.name)

        return {
            "path": args.path,
            "directories": sorted(directories),
            "modified_files": [],
            "files": sorted(files),
        }
