from agent.tools.file_operations.read_file import ReadFileTool
from agent.tools.file_operations.write_file import WriteFileTool
from agent.tools.file_operations.replace_in_file import ReplaceFileTool
from agent.tools.dir_operations.create_dir import CreateDirTool
from agent.tools.dir_operations.list_dir_recursive import ListDirRecursiveTool


TOOLS = {
    "read_file": ReadFileTool(),
    "write_file": WriteFileTool(),
    "replace_in_file": ReplaceFileTool(),
    "create_dir": CreateDirTool(),
    "list_dir_recursive": ListDirRecursiveTool(),
}
