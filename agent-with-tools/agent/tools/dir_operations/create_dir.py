from pathlib import Path
from pydantic import BaseModel
from agent.tools.base import Tool


class CreateDirArgs(BaseModel):
    path: str = "."  # takes the project root by default
    directory_name: str  # folder to be created


class CreateDirTool(Tool):
    name = "create_dir"
    description = (
        "Create one or more nested directories under the given path. "
        "Missing parent directories are created automatically."
    )

    args_schema = CreateDirArgs

    async def execute(self, args: CreateDirArgs):

        dir_path = self.resolve_project_path(args.path)
        project_root = Path.cwd()

        if not dir_path.exists():
            raise FileNotFoundError(f"{args.path} does not exist.")

        if not dir_path.is_dir():
            raise ValueError(f"{args.path} is not a directory.")

        new_path = self.resolve_project_path( str(Path(args.path) / args.directory_name))

        if new_path.exists():
            raise ValueError(f"{args.directory_name} already exists.")

        new_path.mkdir(parents=True)

        return {
            "parent": args.path,
            "directory": args.directory_name,
            "modified_files": [],
            "created_path": str(new_path.relative_to(project_root)),
        }
