from pathlib import Path
from pydantic import BaseModel, Field
from agent.tools.base import Tool


class EditFileArgs(BaseModel):
    path: str = Field(description="Path to the file to edit, relative to project root.")
    old_string: str = Field(
        description=(
            "Exact text to find in the file. Must provide enough surrounding context "
            "for a unique match. If multiple matches are found, the tool will error "
            "asking for more context."
        )
    )
    new_string: str = Field(
        description=(
            "Text to replace old_string with. "
            "To insert code: set old_string to an anchor line and include that same "
            "anchor line in new_string followed by the new code. "
            "To delete code: set new_string to empty string."
        )
    )
    replace_all: bool = Field(
        default=False,
        description="Replace all occurrences of old_string instead of just the first.",
    )


class ReplaceFileTool(Tool):
    name = "edit_file"
    description = (
        "Edit a file by finding an exact block of text and replacing it. "
        "Uses exact string matching — you must provide enough context for a unique match. "
        "This is the primary tool for targeted code changes: replace code, insert new code "
        "(keep the anchor line in both old and new), or delete code (set new_string to empty)."
    )

    args_schema = EditFileArgs

    async def execute(self, args: EditFileArgs):
        if not args.old_string:
            raise ValueError("'old_string' cannot be empty.")

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

        count = content.count(args.old_string)
        if count == 0:
            raise ValueError(
                f"old_string not found in {args.path}. Check indentation and exact text."
            )
        if count > 1 and not args.replace_all:
            raise ValueError(
                f"Found {count} matches. Provide more surrounding lines "
                "in old_string to identify the correct match."
            )

        new_content = content.replace(
            args.old_string, args.new_string, -1 if args.replace_all else 1
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return {
            "path": args.path,
            "modified_files": [args.path],
        }
