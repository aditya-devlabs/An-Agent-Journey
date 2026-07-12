import shutil
import os
import tempfile
from nextjs_agent.tools.base import TOOL
from pydantic import BaseModel, Field
from nextjs_agent.models.exceptions import EditFileToolError


class EditFileToolArgs(BaseModel):
    path: str = Field(description="Path of the file to be read")
    start: int = Field(
        description="Start line from where the file needs to be edited. User facing field. 1-indexed"
    )
    end: int = Field(
        description="End line till where the file needs to be edited. User facing field,Inclusive, 1-indexed"
    )
    content: str = Field(
        description="Content which needs to be placed in the start till end line"
    )


class EditFileTool(TOOL):
    name = "edit_file"
    description = "Edits a file for the given path, start and end line number"

    args_schema = EditFileToolArgs

    async def execute(self, args: EditFileToolArgs):
        if args.start < 1:
            raise EditFileToolError("start must be >= 1")

        if args.end < args.start - 1:
            raise EditFileToolError("end must be >= start - 1 for replace, or end = start - 1 for insert")

        file_path = self.resolve_project_path(args.path)

        if not file_path.exists():
            raise FileNotFoundError(f"{args.path} does not exist.")

        if not file_path.is_file():
            raise ValueError(f"{args.path} is not a file.")

        tmp_fd, tmp_path = tempfile.mkstemp(dir=file_path.parent)

        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as dst, open(file_path, "r", encoding="utf-8") as src:
                line_count = 0
                is_edited = False
                content = args.content

                if content and not content.endswith("\n"):
                    content += "\n"
                for i, line in enumerate(src, 1):
                    line_count = i
                    if i < args.start:
                        dst.write(line)

                    elif i <= args.end:
                        if i == args.start:
                            is_edited = True
                            dst.write(content)
                    elif args.start > args.end and i == args.start:
                        is_edited = True
                        dst.write(content)
                        dst.write(line)

                    else:
                        dst.write(line)

                if args.start > line_count:
                    is_edited = True
                    dst.write(content)

            if not is_edited:
                raise EditFileToolError("File didn't get edited")
            
            shutil.copymode(str(file_path), tmp_path)
            os.replace(tmp_path, str(file_path))
        except EditFileToolError:
            raise
        except Exception as e:
            raise EditFileToolError(f"Failed to edit {args.path}: {e}")
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            
