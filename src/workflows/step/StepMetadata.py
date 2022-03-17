

from abc import ABC
from dataclasses import dataclass
from typing import Any, Optional


### component definitions -----------

@dataclass
class StepMetadata(ABC):
    step_id: int
    tool_name: str
    label: Optional[str]

@dataclass
class InputDataStepMetadata(StepMetadata):
    pass

@dataclass
class ToolStepMetadata(StepMetadata):
    owner: str
    changeset_revision: str
    shed: str
    workflow_outputs: list[dict[str, Any]]

    def get_uri(self) -> str:
        return f'https://{self.shed}/repos/{self.owner}/{self.tool_name}/archive/{self.changeset_revision}.tar.gz'


def init_inputdatastep_metadata(step: dict[str, Any]) -> InputDataStepMetadata:
    return InputDataStepMetadata(
        step_id=step['id'],
        tool_name=step['name'],
        label=step['label']
    )

def init_toolstep_metadata(step: dict[str, Any]) -> ToolStepMetadata:
    return ToolStepMetadata(
        step_id=step['id'],
        tool_name=step['name'],
        label=step['label'],
        owner=step['tool_shed_repository']['owner'],
        changeset_revision=step['tool_shed_repository']['changeset_revision'],
        shed=step['tool_shed_repository']['tool_shed'],
        workflow_outputs=step['workflow_outputs']
    )