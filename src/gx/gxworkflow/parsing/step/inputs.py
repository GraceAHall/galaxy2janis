
from entities.tool.Tool import Tool
from gx.gxtool.param.Param import Param
import logs.logging as logging
from typing import Any

from entities.workflow import Workflow
from entities.workflow import (
    StepInput, 
    StepInputRegister,
    WorkflowInputStepInput,
    ConnectionStepInput,
    RuntimeStepInput,
    StaticStepInput
)

from ..tool_state import load_tool_state


def parse_step_inputs(step: dict[str, Any], tool: Tool, workflow: Workflow) -> StepInputRegister:
    parser = ToolStepInputParser(step, tool, workflow)
    return parser.parse()


### FACTORY ###

def init_workflow_input_step_input(param: Param, details: dict[str, Any]) -> StepInput:
    return WorkflowInputStepInput(
        gxparam=param,
        step_id=details['id']
    )

def init_connection_step_input(param: Param, details: dict[str, Any]) -> StepInput:
    return ConnectionStepInput(
        gxparam=param,
        step_id=details['id'],
        output_name=details['output_name']
    )

def init_runtime_step_input(param: Param) -> StepInput:
    return RuntimeStepInput(
        gxparam=param
    )

def init_static_step_input(param: Param, value: Any) -> StepInput:
    return StaticStepInput(
        gxparam=param,
        value=value
    )


### MAIN LOGIC ###

class ToolStepInputParser:
    def __init__(self, step: dict[str, Any], tool: Tool, workflow: Workflow):
        self.step = step
        self.tool = tool
        self.workflow = workflow
        self.inputs: dict[str, StepInput] = {}

    def parse(self) -> StepInputRegister:
        self.parse_step_input_connections()
        self.parse_step_inputs()
        self.parse_step_tool_state()

        inputs = list(self.inputs.values())
        register = StepInputRegister()
        for inp in inputs:
            register.add(inp)
        return register

    def parse_step_input_connections(self) -> None:
        for name, details in self.step['input_connections'].items(): #type: ignore
            name = name.replace('|', '.')
            param = self.tool.get_gxparam(name)
            assert(param)
            if isinstance(details, list):  # ignore array connection inputs
                logging.workflow_step_array_connections()
            else:
                step_id = details['id']
                if self.workflow.get_input(step_id=step_id):
                    self.inputs[param.name] = init_workflow_input_step_input(param, details)
                else:
                    self.inputs[param.name] = init_connection_step_input(param, details)

    def parse_step_inputs(self) -> None:
        inputs: list[str] = [inp['name'] for inp in self.step['inputs']]
        inputs: list[str] = [inp for inp in inputs if inp not in self.inputs]
        for name in inputs:
            name = name.replace('|', '.')
            param = self.tool.get_gxparam(name)
            assert(param)
            self.inputs[param.name] = init_runtime_step_input(param)

    def parse_step_tool_state(self) -> None:
        self.step['tool_state'] = load_tool_state(self.step)
        for name, value in self.step['tool_state'].items(): #type: ignore
            name = name.replace('|', '.')
            if name not in self.inputs:
                if not name.endswith('__'):
                    param = self.tool.get_gxparam(name)
                    assert(param)
                    if value == 'RuntimeValue':
                        self.inputs[param.name] = init_runtime_step_input(param)
                    else:
                        self.inputs[param.name] = init_static_step_input(param, value)

