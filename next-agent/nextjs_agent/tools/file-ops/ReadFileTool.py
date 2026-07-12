from itertools import islice
from nextjs_agent.tools.base import TOOL
from pydantic import Field, BaseModel


class ReadFileArgs(BaseModel):
    path: str = Field(description="Path of the file to be read")
    start: int | None = Field(default=1, description="Start line from where the file is to be read. User facing field. 1-indexed")
    end: int | None = Field(default=None, description="End line till where the file is to be read. User facing field. Inclusive, 1-indexed")

class ReadFileTool(TOOL):
    name = "read_file"
    description = "Reads a file from the project"

    args_schema = ReadFileArgs

    async def execute(self, args: ReadFileArgs):

        file_path = self.resolve_project_path(args.path)

        if not file_path.exists():
            raise FileNotFoundError(f"{args.path} does not exist.")

        if not file_path.is_file():
            raise ValueError(f"{args.path} is not a file.")
        
        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                internal_start = (args.start - 1) if args.start else 0
                internal_end= args.end + 1 if args.end else None
                lines =    islice(f, internal_start, internal_end)

                content =  "".join(lines)

                return {
                    "path": args.path,
                    "content": content,
                    "modified_files": []
                }
        except UnicodeDecodeError:
            raise ValueError("The file is not a UTF-8 text file.")
