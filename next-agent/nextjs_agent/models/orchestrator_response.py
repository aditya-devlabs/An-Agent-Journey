from pydantic import BaseModel, Field
from nextjs_agent.models.task import Task


class OrchestratorResponse(BaseModel):
    thought: str = Field(description="What the orchestrator is thinking about the progress.")
    task: Task | None = Field(description="Next atomic task to execute. None when done.")
    done: bool = Field(description="True when user's request is fully completed.")
    reason: str | None = Field(default=None, description="Why done or why this task.")
