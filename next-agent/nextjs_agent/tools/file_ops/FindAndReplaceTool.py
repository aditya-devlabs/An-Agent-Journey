from nextjs_agent.models.exceptions import FindAndReplaceToolError
import shutil
import os
import tempfile
from nextjs_agent.tools.base import TOOL
from pydantic import BaseModel, Field


class FindAndReplaceToolArgs(BaseModel):
    path: str = Field(
        description="Path of the file where find and replace operation will occur."
    )
    find: str = Field(
        description="Exact content that needs to be replaced in the file."
    )
    replace: str = Field(description="Content that will replace the original content")
    replace_all: bool = Field(
        description="Tells if all the occurrences needs to be replaced or not."
    )


class FindAndReplaceTool(TOOL):
    name = "find_and_replace"
    description = "Replace exact text in a file. Use for renaming variables, swapping function names, inserting new content, appending at EOF, or targeted text substitution."

    args_schema = FindAndReplaceToolArgs

    async def execute(self, args: FindAndReplaceToolArgs):

        file_path = self.resolve_project_path(args.path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(
                f"File with given path: {file_path} doesn't exits in the project."
            )
        if not file_path.is_file():
            raise ValueError(f"{args.path} is not a file.")

        content = file_path.read_text(encoding="utf-8")

        count = content.count(args.find)

        if count == 0:
            raise ValueError(f"{args.find} not found in {args.path}")

        if args.replace_all:
            new_content = content.replace(args.find, args.replace)
        else:
            new_content = content.replace(args.find, args.replace, 1)

        tmp_fd, tmp_path = tempfile.mkstemp(dir=file_path.parent)

        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as dst:
                dst.write(new_content)

            shutil.copymode(str(file_path), tmp_path)
            os.replace(tmp_path, str(file_path))

            replaced = count if args.replace_all else 1
            return {
                "success": True,
                "summary": f"Replaced {replaced} occurrences of '{args.find}' → '{args.replace}'",
                "modified_files": [args.path],
            }
        except Exception as e:
            raise FindAndReplaceToolError(
                f"Failed to find: {args.find}  and replace: {args.replace} for path: {args.path}. Error occurred: {e}"
            )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
