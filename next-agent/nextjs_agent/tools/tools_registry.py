from nextjs_agent.tools.file_ops.ReadFileTool import ReadFileTool
from nextjs_agent.tools.file_ops.WriteFileTool import WriteFileTool
from nextjs_agent.tools.file_ops.FindAndReplaceTool import FindAndReplaceTool
from nextjs_agent.tools.file_ops.EditFileTool import EditFileTool
from nextjs_agent.tools.file_ops.DeleteFileTool import DeleteFileTool

from nextjs_agent.tools.dir_ops.CreateDirTool import CreateDirTool
from nextjs_agent.tools.dir_ops.ListDirTool import ListDirTool

from nextjs_agent.tools.package_tools.AddPackageTool import AddPackageTool
from nextjs_agent.tools.package_tools.RemovePackageTool import RemovePackageTool



TOOLS = {
    "read_file": ReadFileTool(),
    "write_file": WriteFileTool(),
    "find_and_replace": FindAndReplaceTool(),
    "edit_file": EditFileTool(),
    "delete_file": DeleteFileTool(),

    "create_dir": CreateDirTool(),
    "list_dir": ListDirTool(),

    "add_package": AddPackageTool(),
    "remove_package": RemovePackageTool()
    
}

def get_tools_schema() -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.args_schema.model_json_schema(),
            },
        }
        for tool in TOOLS.values()
    ]