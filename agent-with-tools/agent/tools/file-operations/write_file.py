from pathlib import Path
from typing import Literal
from pydantic import BaseModel
from agent.tools.base import Tool


class WriteFileArgs(BaseModel):
    path: str
    content: str
    mode: Literal["write", "append"] = "write"


class WriteFileTool(Tool):
    name = "write_file"
    description = (
        "Write UTF-8 text to a file. "
        "Use mode='write' to overwrite or create a file, "
        "or mode='append' to append to an existing file."
    )

    args_schema = WriteFileArgs

    async def execute(self, args: WriteFileArgs):

        project_root = Path.cwd()
        file_path = (project_root / args.path).resolve()

        if project_root not in file_path.parents and file_path != project_root:
            raise ValueError("Cannot access files outside the project.")

        if args.mode != "write" and not file_path.exists():
            raise FileNotFoundError(f"{args.path} does not exist.")

        if file_path.exists() and not file_path.is_file():
            raise ValueError(f"{args.path} is not a file.")

        _mode = "w" if args.mode == "write" else "a"
        with open(file_path, _mode, encoding="utf-8") as f:
            f.write(args.content)
        return {
            "path": args.path,
            "mode": args.mode,
            "bytes_written": len(args.content),
        }
