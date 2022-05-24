

from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class StepMetadata:
    uuid: str
    step_id: int
    step_name: str
    tool_id: str
    tool_state: dict[str, Any]
    is_inbuilt: bool
    workflow_outputs: list[dict[str, Any]]
    repo_name: Optional[str] = None
    label: Optional[str] = None
    owner: Optional[str] = None
    changeset_revision: Optional[str] = None
    shed: Optional[str] = None
    tool_definition_path: Optional[str] = None

    def get_build_url(self) -> str:
        return f'https://{self.shed}/repos/{self.owner}/{self.repo_name}/archive/{self.changeset_revision}.tar.gz'
    
    # a method which uses version instead of build?
    def get_uri_version(self) -> str:
        raise NotImplementedError()

