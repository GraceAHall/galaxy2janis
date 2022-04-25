

from typing import Any

from workflows.step.WorkflowStep import WorkflowStep
from workflows.step.inputs.StepInput import StepInput, init_connection_step_input, init_static_step_input, init_runtime_step_input, init_workflow_input_step_input
from workflows.step.inputs.StepInputRegister import StepInputRegister
from workflows.step.outputs.StepOutputRegister import StepOutputRegister
from workflows.step.outputs.StepOutput import init_tool_step_output
from workflows.step.metadata.StepMetadata import StepMetadata
from workflows.workflow.Workflow import Workflow
from .ToolStateFlattener import ToolStateFlattener



class ToolStepParser:
    def __init__(self, workflow: Workflow) -> None:
        self.workflow = workflow
        self.inputs: dict[str, StepInput] = {}
        self.flattened_tool_state: dict[str, Any] = {}

    def parse(self, step: dict[str, Any]) -> WorkflowStep:
        self.gxstep = step
        return WorkflowStep(
            metadata=self.get_step_metadata(),
            inputs=self.get_step_inputs(),
            outputs=self.get_step_outputs()
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
            is_inbuilt=False,
            workflow_outputs=self.gxstep['workflow_outputs'],
            label=self.gxstep['label'],
            owner=self.gxstep['tool_shed_repository']['owner'],
            changeset_revision=self.gxstep['tool_shed_repository']['changeset_revision'],
            shed=self.gxstep['tool_shed_repository']['tool_shed'],
        )

    def get_step_inputs(self) -> StepInputRegister:
        self.inputs = {}
        self.set_flattened_tool_state()
        self.parse_connection_inputs()
        self.parse_static_inputs()
        self.parse_user_defined_inputs()
        step_inputs = list(self.inputs.values())
        return StepInputRegister(step_inputs) 

    def set_flattened_tool_state(self) -> None:
        flattener = ToolStateFlattener()
        self.flattened_tool_state = flattener.flatten(self.gxstep)

    def parse_connection_inputs(self) -> None:
        for name, details in self.gxstep['input_connections'].items():
            step_id = details['id']
            if self.workflow.get_input(step_id=step_id):
                self.inputs[name] = init_workflow_input_step_input(name, details)
            else:
                self.inputs[name] = init_connection_step_input(name, details)

    def parse_static_inputs(self) -> None:
        for name, value in self.flattened_tool_state.items():
            if name not in self.inputs:
                if not name.endswith('__') and value != 'RuntimeValue':
                    self.inputs[name] = init_static_step_input(name, value)

    def parse_user_defined_inputs(self) -> None:
        for name, value in self.flattened_tool_state.items():
            if name not in self.inputs:
                if value == 'RuntimeValue':
                    self.inputs[name] = init_runtime_step_input(name)

    def get_step_outputs(self) -> StepOutputRegister:
        step_outputs = [init_tool_step_output(self.gxstep, out) for out in self.gxstep['outputs']]
        return StepOutputRegister(step_outputs)
