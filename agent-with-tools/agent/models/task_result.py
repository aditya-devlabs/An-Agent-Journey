from pydantic import BaseModel, Field

class TaskResult(BaseModel):
    success: bool
    summary: str = Field(description="Breif summary of what was done.")

    modified_files: list[str] = Field(default_factory=list)
    error:str|None = None