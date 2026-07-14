from pydantic import BaseModel, Field


class FunctionCall(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str
    function: FunctionCall


class AssistantResponse(BaseModel):
    content: str | None = None
    tool_calls: list[ToolCall] | None = None
