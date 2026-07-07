from pathlib import Path
import os
from pydantic import BaseModel
from agent.tools.base import Tool

class ReadFileArgs(BaseModel):
    path: str

class ReadFileTool(Tool):
    name = "read_file"
    description = "Read a file from the project."

    args_schema = ReadFileArgs

    async def execute(self, args: ReadFileArgs):
        
        file_path = self.resolve_project_path(args.path)

        if not file_path.exists():
            raise FileNotFoundError(f"{args.path} does not exist.")

        if not file_path.is_file():
            raise ValueError(f"{args.path} is not a file.")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "path": args.path,
                "content": content,
                "modified_files": [],
            }

        except UnicodeDecodeError:
            raise ValueError("The file is not a UTF-8 text file.")