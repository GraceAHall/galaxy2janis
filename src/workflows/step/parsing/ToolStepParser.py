

from typing import Any

from workflows.step.WorkflowStep import WorkflowStep
from workflows.step.inputs.StepInput import StepInput
from workflows.step.metadata.StepMetadata import StepMetadata
from workflows.workflow.Workflow import Workflow

from .inputs import parse_step_inputs
from .outputs import parse_step_outputs


class ToolStepParser:
    def __init__(self, workflow: Workflow) -> None:
        self.workflow = workflow
        self.inputs: dict[str, StepInput] = {}
        self.flattened_tool_state: dict[str, Any] = {}

    def parse(self, step: dict[str, Any]) -> WorkflowStep:
        self.gxstep = step
        return WorkflowStep(
            metadata=self.get_step_metadata(),
            inputs=parse_step_inputs(self.gxstep, self.workflow),
            outputs=parse_step_outputs(self.gxstep)
        )

    def get_step_metadata(self) -> StepMetadata:
        if 'tool_shed_repository' not in self.gxstep:
            return self.get_step_metadata_builtin()
        else:
            return self.get_step_metadata_repo()

    def get_step_metadata_builtin(self) -> StepMetadata:
        return StepMetadata(
            uuid=self.gxstep['uuid'],
            step_id=self.gxstep['id'],
            step_name=self.gxstep['name'],
            tool_id=self.gxstep['tool_id'],
            tool_state=self.gxstep['tool_state'], 
            is_inbuilt=True,
            workflow_outputs=self.gxstep['workflow_outputs'],
            label=self.gxstep['label'],
            owner=None,
            changeset_revision=None,
            shed=None,
        )
    
    def get_step_metadata_repo(self) -> StepMetadata:
        'toolshed.g2.bx.psu.edu/repos/devteam/picard/picard_MarkDuplicates/2.18.2.1'
        repo_url_split = self.gxstep['tool_id'].split('/')
        tool_id = repo_url_split[4]
        return StepMetadata(
            uuid=self.gxstep['uuid'],
            step_id=self.gxstep['id'],
            step_name=self.gxstep['name'],
            repo_name=self.gxstep['tool_shed_repository']['name'],
            tool_id=tool_id,
            tool_state=self.gxstep['tool_state'],
            is_inbuilt=False,
            workflow_outputs=self.gxstep['workflow_outputs'],
            label=self.gxstep['label'],
            owner=self.gxstep['tool_shed_repository']['owner'],
            changeset_revision=self.gxstep['tool_shed_repository']['changeset_revision'],
            shed=self.gxstep['tool_shed_repository']['tool_shed'],
        )
