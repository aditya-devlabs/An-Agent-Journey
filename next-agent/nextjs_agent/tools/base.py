from pathlib import Path
from pydantic import BaseModel
from abc import ABC, abstractmethod


class TOOL(ABC):
    name: str
    description: str

    args_schema: type[BaseModel]

    def __init__(self, project_root: Path):
        self.project_root = project_root

    @abstractmethod
    def execute(self, args):
        pass

    def resolve_project_path(self, path: str) -> Path:
        resolved = (self.project_root / path).resolve()

        if self.project_root not in resolved.parents and resolved != self.project_root:
            raise ValueError("Cannot access files outside the project.")

        return resolved
