from pathlib import Path
from pydantic import BaseModel
from agent.tools.base import Tool

class ListDirArgs(BaseModel):
    path: str

class ListDirTool(Tool):
    name = "list_dir"
    description = ("Lists all the directories ")

    args_schema = ListDirArgs

    async def execute(self, args: ListDirArgs):
        
        project_root = Path.cwd()
        dir_path = (project_root / args.path).resolve()

        if project_root not in dir_path.parents and dir_path != project_root:
            raise ValueError("Cannot access files outside the project.")

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
        
        