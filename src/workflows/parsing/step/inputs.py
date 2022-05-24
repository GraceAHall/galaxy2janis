

from typing import Any

from runtime.settings.ExeSettings import ToolExeSettings
from workflows.parsing.tool_state.load import load_tool_state
from workflows.entities.workflow.workflow import Workflow
from workflows.entities.step.inputs import (
    StepInput, 
    StepInputRegister,
    WorkflowInputStepInput,
    ConnectionStepInput,
    RuntimeStepInput,
    StaticStepInput
)


def parse_step_inputs(step: dict[str, Any], workflow: Workflow, esettings: ToolExeSettings) -> StepInputRegister:
    step['tool_state'] = load_tool_state(esettings, step)
    parser = ToolStepInputParser(step, workflow)
    inputs = parser.parse()
    return StepInputRegister(inputs)

def init_workflow_input_step_input(name: str, details: dict[str, Any]) -> StepInput:
    name = name.replace('|', '.')
    return WorkflowInputStepInput(
        gxvarname=name,
        step_id=details['id']
    )

def init_connection_step_input(name: str, details: dict[str, Any]) -> StepInput:
    name = name.replace('|', '.')
    return ConnectionStepInput(
        gxvarname=name,
        step_id=details['id'],
        output_name=details['output_name']
    )

def init_runtime_step_input(name: str) -> StepInput:
    return RuntimeStepInput(
        gxvarname=name
    )

def init_static_step_input(name: str, value: Any) -> StepInput:
    return StaticStepInput(
        gxvarname=name,
        value=value
    )


class ToolStepInputParser:
    def __init__(self, gxstep: dict[str, Any], workflow: Workflow):
        self.gxstep = gxstep
        self.workflow = workflow
        self.inputs: dict[str, StepInput] = {}

    def parse(self) -> list[StepInput]:
        self.parse_connection_inputs()
        self.parse_static_inputs()
        self.parse_user_defined_inputs()
        return list(self.inputs.values())

    def parse_connection_inputs(self) -> None:
        for name, details in self.gxstep['input_connections'].items(): #type: ignore
            step_id = details['id']
            if self.workflow.get_input(step_id=step_id):
                self.inputs[name] = init_workflow_input_step_input(name, details)
            else:
                self.inputs[name] = init_connection_step_input(name, details)

    def parse_static_inputs(self) -> None:
        for name, value in self.gxstep['tool_state'].items(): #type: ignore
            if name not in self.inputs:
                if not name.endswith('__') and value != 'RuntimeValue':
                    self.inputs[name] = init_static_step_input(name, value)

    def parse_user_defined_inputs(self) -> None:
        for name, value in self.gxstep['tool_state'].items(): #type: ignore
            if name not in self.inputs:
                if value == 'RuntimeValue':
                    self.inputs[name] = init_runtime_step_input(name)

