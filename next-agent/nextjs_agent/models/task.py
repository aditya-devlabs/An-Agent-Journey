from pydantic import BaseModel, Field

# will be used for convo between main and worker agent


class Task(BaseModel):
    goal: str = Field(description="The task to accomplish.")

    context: str | None = Field(
        default=None, description="Additional context or instructions."
    )

    relevant_files: list[str] = Field(
        default_factory=list, description="Files the worker should consider first."
    )
