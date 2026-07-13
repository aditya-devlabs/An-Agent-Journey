from nextjs_agent.models.exceptions import DeleteFileToolError
import os
from nextjs_agent.tools.base import TOOL
from pydantic import BaseModel, Field

class DeleteFileToolArgs(BaseModel):
    path: str = Field(description="path of the file relative to the root of the project which needs to be deleted.")


class DeleteFileTool(TOOL):
    name = "delete_file"
    description = "Deletes the file for the given path."
    args_schema = DeleteFileToolArgs

    async def execute(self, args: DeleteFileToolArgs):
        
        file_path = self.resolve_project_path(args.path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"{args.path} does not exist.")

        if not file_path.is_file():
            raise ValueError(f"{args.path} is not a file.")
        
        try:
            os.remove(file_path)

            return {
                    "success": True,
                    "summary": f"Deleted {args.path}",
                    "modified_files": [args.path]
                }
        except Exception as e:
            raise DeleteFileToolError(f"Error occurred while deleting the file with path: {args.path}. Error occurred : {e}")
