import subprocess
from nextjs_agent.models.exceptions import AddPackageToolError, RemovePackageToolError
from pathlib import Path
from nextjs_agent.tools.base import TOOL
from pydantic import BaseModel, Field
from nextjs_agent.tools.package_tools.detect_manager import detect_manager


class RemovePackageToolArgs(BaseModel):
    package: str = Field(
        description="Name of package that needs to be removed from the nextjs package.json"
    )


class RemovePackageTool(TOOL):
    name = "remove_package"
    description = (
        "use to remove package from the package.json of the nextjs project folder."
    )

    args_schema = RemovePackageToolArgs

    async def execute(self, args: RemovePackageToolArgs):

        project_root = Path.cwd()

        manager = detect_manager(project_root)

        cmd = {
            "npm": f"npm uninstall {args.package}",
            "pnpm": f"pnpm remove {args.package}",
            "yarn": f"yarn remove {args.package}",
            "bun": f"bun remove {args.package}",
        }
        try:
            result = subprocess.run(
                cmd[manager],
                shell=True,
                capture_output=True,
                text=True,
                cwd=project_root,
            )
            if result.returncode != 0:
                raise Exception(result.stderr)

            return {
                "success": True,
                "summary": f"Removed {args.package} using {manager}",
                "modified_files": [
                    "package.json",
                    {"npm": "package-lock.json", "pnpm": "pnpm-lock.yaml", "yarn": "yarn.lock", "bun": "bun.lockb"}[manager],
                ],
            }
        except Exception as e:
            raise RemovePackageToolError(f"Failed to remove {args.package}: {e}")
