from pathlib import Path
from pydantic import BaseModel
from agent.tools.base import Tool


class ReplaceFileArgs(BaseModel):
    path: str
    find: str
    replace: str
    replace_all: bool = False


class ReplaceFileTool(Tool):
    name = "replace_in_file"
    description = (
        "Replace text in a UTF-8 file. By default replaces only the first occurrence; "
        "set replace_all=True to replace every occurrence."
    )

    args_schema = ReplaceFileArgs

    async def execute(self, args: ReplaceFileArgs):
        if not args.find:
            raise ValueError("'find' cannot be empty.")

        file_path = self.resolve_project_path(args.path)

        if not file_path.exists():
            raise FileNotFoundError(f"{args.path} does not exist.")

        if not file_path.is_file():
            raise ValueError(f"{args.path} is not a file.")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            raise ValueError("The file is not a UTF-8 text file.")

        if args.find not in content:
            raise ValueError("The specified text was not found in the file.")

        occurrences = content.count(args.find)
        if args.replace_all:
            new_content = content.replace(args.find, args.replace)
            replaced_count = occurrences
        else:
            new_content = content.replace(args.find, args.replace, 1)
            replaced_count = 1

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return {
            "path": args.path,
            "found_string": args.find,
            "replaced_with": args.replace,
            "occurrences_replaced": replaced_count,
        }
