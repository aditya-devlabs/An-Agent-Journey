from typing import Literal
from nextjs_agent.models.exceptions import FileAlreadyExistsError, WriteFileToolError
from nextjs_agent.tools.base import TOOL
from pydantic import Field
from pydantic import BaseModel


class WriteFileToolArgs(BaseModel):
    path: str = Field(
        description="Path of the file that needs to be created or needs to be overwritten. If file doesnt present then it will be created automatically with this tool."
    )
    content: str = Field(
        description="Content to be placed in this newly created file or the content to overwrite the entire file."
    )
    mode: Literal["write", "overwrite"] = Field(
        description="Tells if the mode is write or overwrite. Use 'write' when file needs to be created. Use 'overwrite' when file needs to be overwritten."
    )


class WriteFileTool(TOOL):
    name = "write_file"
    description = "Create a new file or overwrite an existing one and places content inside it."

    args_schema = WriteFileToolArgs

    async def execute(self, args: WriteFileToolArgs):

        file_path = self.resolve_project_path(args.path).resolve()

        if args.mode == "write"  and file_path.exists():
            raise FileAlreadyExistsError(
                f"File with the given path: {args.path} already exists!"
            )

        content = args.content
        if content and not content.endswith("\n"):
            content += "\n"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
             
            if args.mode == "write":
                summary = f"Created '{args.path}'"
            else:
                summary = f"Overwrote '{args.path}'"

            return {
                    "success": True,
                    "summary": summary,
                    "modified_files": [args.path]
                }
        except Exception as e:
            raise WriteFileToolError(
                f"Error occurred while writing in the file. Error : {e}"
            )
