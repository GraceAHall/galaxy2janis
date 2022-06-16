
import runtime.logging.logging as logging
from typing import Any

from runtime.settings.ExeSettings import ToolExeSettings
from workflows.parsing.tool_state import load_tool_state
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
    parser = ToolStepInputParser(step, workflow, esettings)
    return parser.parse()


# StepInput object factory
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

# main class
class ToolStepInputParser:
    def __init__(self, step: dict[str, Any], workflow: Workflow, esettings: ToolExeSettings):
        self.step = step
        self.workflow = workflow
        self.esettings = esettings
        self.inputs: dict[str, StepInput] = {}

    def parse(self) -> StepInputRegister:
        self.parse_step_input_connections()
        self.parse_step_inputs()
        self.parse_step_tool_state()
        inputs = list(self.inputs.values())
        return StepInputRegister(inputs)

    def parse_step_input_connections(self) -> None:
        for name, details in self.step['input_connections'].items(): #type: ignore
            if isinstance(details, list):  # ignore array connection inputs
                logging.workflow_step_array_connections()
            else:
                step_id = details['id']
                if self.workflow.get_input(step_id=step_id):
                    self.inputs[name] = init_workflow_input_step_input(name, details)
                else:
                    self.inputs[name] = init_connection_step_input(name, details)

    def parse_step_inputs(self) -> None:
        inputs: list[str] = [inp['name'] for inp in self.step['inputs']]
        inputs: list[str] = [inp for inp in inputs if inp not in self.inputs]
        for name in inputs:
            self.inputs[name] = init_runtime_step_input(name)

    def parse_step_tool_state(self) -> None:
        self.step['tool_state'] = load_tool_state(self.esettings, self.step)
        for name, value in self.step['tool_state'].items(): #type: ignore
            if name not in self.inputs:
                if not name.endswith('__'):
                    if value == 'RuntimeValue':
                        self.inputs[name] = init_runtime_step_input(name)
                    else:
                        self.inputs[name] = init_static_step_input(name, value)

