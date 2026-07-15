from re import L


class WorkerError(Exception):
    """Base exception for worker failures."""


class MaxRetriesExceededError(WorkerError):
    """Worker exceeded the maximum number of recoverable errors."""


class MaxIterationsExceededError(WorkerError):
    """Worker exceeded the maximum number of execution iterations."""


class UnknownToolError(WorkerError):
    """The model requested a tool that is not registered."""


class InvalidAssistantResponseError(WorkerError):
    """The assistant response did not match the expected schema."""


class InvalidToolArgumentsError(WorkerError):
    """The tool arguments failed schema validation."""


class ToolExecutionError(WorkerError):
    """The requested tool failed during execution."""


class FileAlreadyExistsError(WorkerError):
    """File with given path already exists."""


class WriteFileToolError(WorkerError):
    """Error occurred while writing in the file."""


class FindAndReplaceToolError(WorkerError):
    """Error occurred while using find and replace tool."""


class DeleteFileToolError(WorkerError):
    """Error occurred while using deleting the file."""


class DirectoryAlreadyExistsError(WorkerError):
    """Directory with given path already exists."""


class CreateDirToolError(WorkerError):
    """Error occurred while creating the directory."""


class ListDirToolError(WorkerError):
    """Error occurred while traversing the directory."""


class AddPackageToolError(WorkerError):
    """Error occurred while adding the package"""


class RemovePackageToolError(WorkerError):
    """Error occurred while removing the package"""


class SearchCodeToolError(WorkerError):
    """Error occurred while searching file contents."""
