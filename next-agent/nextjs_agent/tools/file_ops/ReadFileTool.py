from itertools import islice
from nextjs_agent.tools.base import TOOL
from pydantic import Field, BaseModel


class ReadFileToolArgs(BaseModel):
    path: str = Field(description="Path of the file to be read")
    start: int | None = Field(default=1, description="Start line from where the file is to be read. User facing field. 1-indexed")
    end: int | None = Field(default=None, description="End line till where the file is to be read. User facing field. Inclusive, 1-indexed")

class ReadFileTool(TOOL):
    name = "read_file"
    description = "Read a file's content from the project. Use start/end for line ranges."

    args_schema = ReadFileToolArgs

    async def execute(self, args: ReadFileToolArgs):

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
                line_count = content.count("\n") + 1
                return {
                    "success": True,
                    "summary": f"Read '{args.path}' ({line_count} lines)",
                    "content": content,
                    "modified_files": []
                }
        except UnicodeDecodeError:
            raise ValueError("The file is not a UTF-8 text file.")
