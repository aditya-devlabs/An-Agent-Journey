from nextjs_agent.models.exceptions import DirectoryAlreadyExistsError, CreateDirToolError
import os
from nextjs_agent.tools.base import TOOL
from pydantic import BaseModel, Field


class CreateDirToolArgs(BaseModel):
    path: str = Field(description="Path of the directory that needs to be created.")


class CreateDirTool(TOOL):
    name = "create_dir"
    description = "Creates a new directory with the given path under the root folder."

    args_schema = CreateDirToolArgs

    async def execute(self, args: CreateDirToolArgs):

        dir_path = self.resolve_project_path(args.path).resolve()

        if dir_path.exists() and dir_path.is_dir():
            return {
                "success": True,
                "summary": f"Directory '{args.path}' already exists.",
                "modified_files": []
            }
        
        if dir_path.exists() and dir_path.is_file():
            raise ValueError(f"'{args.path}' is a file, not a directory'")

        try:
            dir_path.mkdir(parents=True, exist_ok=True)

            return {
                "success": True,
                "summary": f"Directory '{args.path}' created successfully.",
                "modified_files": []
            }
        except OSError as e:
            raise CreateDirToolError(f"Failed to create directory '{args.path}': {e}")