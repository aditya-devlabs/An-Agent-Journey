from pathlib import Path
from nextjs_agent.tools.file_ops.ReadFileTool import ReadFileTool
from nextjs_agent.tools.file_ops.WriteFileTool import WriteFileTool
from nextjs_agent.tools.file_ops.FindAndReplaceTool import FindAndReplaceTool
from nextjs_agent.tools.file_ops.DeleteFileTool import DeleteFileTool

from nextjs_agent.tools.dir_ops.CreateDirTool import CreateDirTool
from nextjs_agent.tools.dir_ops.ListDirTool import ListDirTool

from nextjs_agent.tools.search.SearchCodeTool import SearchCodeTool

from nextjs_agent.tools.package_tools.AddPackageTool import AddPackageTool
from nextjs_agent.tools.package_tools.RemovePackageTool import RemovePackageTool

from nextjs_agent.tools.skill_tools.ListSkillsTool import ListSkillsTool
from nextjs_agent.tools.skill_tools.ReadSkillTool import ReadSkillTool


def create_tools(project_root: Path) -> dict:
    return {
        "read_file": ReadFileTool(project_root),
        "write_file": WriteFileTool(project_root),
        "find_and_replace": FindAndReplaceTool(project_root),
        "delete_file": DeleteFileTool(project_root),
        "create_dir": CreateDirTool(project_root),
        "list_dir": ListDirTool(project_root),
        "search_code": SearchCodeTool(project_root),
        "add_package": AddPackageTool(project_root),
        "remove_package": RemovePackageTool(project_root),
        "list_skills": ListSkillsTool(project_root),
        "read_skill": ReadSkillTool(project_root),
    }


def get_tools_schema(tools: dict) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.args_schema.model_json_schema(),
            },
        }
        for tool in tools.values()
    ]
