

from dataclasses import dataclass
from typing import Any, Optional

### component definitions -----------

@dataclass
class StepMetadata:
    step_id: int
    uuid: str
    step_name: str
    label: Optional[str]
    tool_name: str
    owner: str
    changeset_revision: str
    shed: str
    workflow_outputs: list[dict[str, Any]]
    tool_definition_path: Optional[str] = None

    def get_uri(self) -> str:
        return f'https://{self.shed}/repos/{self.owner}/{self.tool_name}/archive/{self.changeset_revision}.tar.gz'
