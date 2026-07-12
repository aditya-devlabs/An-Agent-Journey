from pydantic import Field


class AgentState:
    task: str = Field(description="Task given to the agent")
    messages: list[dict]
    branch: str | None
    status: str
    modified_files: list[str]
    error: str | None
