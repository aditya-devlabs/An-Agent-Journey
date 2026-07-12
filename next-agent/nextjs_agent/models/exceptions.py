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


class EditFileToolError(WorkerError):
    """Some error occurred while editing the file."""