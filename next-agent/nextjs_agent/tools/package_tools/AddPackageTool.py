import subprocess
from nextjs_agent.models.exceptions import AddPackageToolError
from pathlib import Path
from nextjs_agent.tools.base import TOOL
from pydantic import BaseModel, Field
from nextjs_agent.tools.package_tools.detect_manager import detect_manager


class AddPackageToolArgs(BaseModel):
    package: str = Field(
        description="Name of package that needs to be added in the nextjs package.json"
    )


class AddPackageTool(TOOL):
    name = "add_package"
    description = (
        "use to add package in the package.json of the nextjs project folder."
    )

    args_schema = AddPackageToolArgs

    async def execute(self, args: AddPackageToolArgs):

        project_root = Path.cwd()

        manager = detect_manager(project_root)

        cmd = {
            "npm": f"npm install {args.package}",
            "pnpm": f"pnpm add {args.package}",
            "yarn": f"yarn add {args.package}",
            "bun": f"bun add {args.package}",
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
                "summary": f"Installed {args.package} using {manager}",
                "modified_files": [
                    "package.json",
                    {"npm": "package-lock.json", "pnpm": "pnpm-lock.yaml", "yarn": "yarn.lock", "bun": "bun.lockb"}[manager],
                ],
            }
        except Exception as e:
            raise AddPackageToolError(f"Failed to install {args.package}: {e}")
