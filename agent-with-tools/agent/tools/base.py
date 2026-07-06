from pathlib import Path
from abc import ABC, abstractmethod
from pydantic import BaseModel


class Tool(ABC):
    name: str
    description: str
    args_schema: type[BaseModel]

    @abstractmethod
    async def execute(self, args): ...

    @staticmethod
    def resolve_project_path(path: str) -> Path:
        project_root = Path.cwd()
        resolved = (project_root / path).resolve()
    
        if project_root not in resolved.parents and resolved != project_root:
            raise ValueError("Cannot access files outside the project.")
    
        return resolved