

from abc import ABC
from dataclasses import dataclass
from typing import Any, Optional


### component definitions -----------

@dataclass
class StepMetadata(ABC):
    step_id: int
    step_name: str
    label: Optional[str]

@dataclass
class InputDataStepMetadata(StepMetadata):
    pass

@dataclass
class ToolStepMetadata(StepMetadata):
    tool_name: str
    owner: str
    changeset_revision: str
    shed: str
    workflow_outputs: list[dict[str, Any]]

    def get_uri(self) -> str:
        return f'https://{self.shed}/repos/{self.owner}/{self.tool_name}/archive/{self.changeset_revision}.tar.gz'

# NOTE this assumes only single input for an InputDataStep
# unsure whether this is always true.
def init_inputdatastep_metadata(step: dict[str, Any]) -> InputDataStepMetadata:
    return InputDataStepMetadata(
        step_id=step['id'],
        step_name=step['inputs'][0]['name'],
        label=step['label']
    )

def init_toolstep_metadata(step: dict[str, Any]) -> ToolStepMetadata:
    return ToolStepMetadata(
        step_id=step['id'],
        step_name=step['name'],
        tool_name=step['tool_shed_repository']['name'],
        label=step['label'],
        owner=step['tool_shed_repository']['owner'],
        changeset_revision=step['tool_shed_repository']['changeset_revision'],
        shed=step['tool_shed_repository']['tool_shed'],
        workflow_outputs=step['workflow_outputs']
    )