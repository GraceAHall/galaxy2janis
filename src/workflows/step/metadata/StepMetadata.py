

from dataclasses import dataclass
from typing import Any, Optional

### component definitions -----------

@dataclass
class StepMetadata:
    step_id: int
    uuid: str
    step_name: str
    tool_id: str
    workflow_outputs: list[dict[str, Any]]
    is_inbuilt: bool
    label: Optional[str] = None
    owner: Optional[str] = None
    changeset_revision: Optional[str] = None
    shed: Optional[str] = None
    tool_definition_path: Optional[str] = None

    def get_uri(self) -> str:
        return f'https://{self.shed}/repos/{self.owner}/{self.tool_id}/archive/{self.changeset_revision}.tar.gz'



