


from abc import ABC, abstractmethod

from typing import Any, Optional

from workflows.step.WorkflowStep import WorkflowStep, InputDataStep, ToolStep
from workflows.step.inputs.StepInput import StepInput, init_connection_step_input, init_static_step_input, init_runtime_step_input
from workflows.step.inputs.StepInputRegister import StepInputRegister
from workflows.step.outputs.StepOutputRegister import StepOutputRegister
from workflows.step.outputs.StepOutput import init_input_step_output, init_tool_step_output
from workflows.step.metadata.StepMetadata import (
    ToolStepMetadata,
    init_inputdatastep_metadata, 
    init_toolstep_metadata
)
from .ToolStateFlattener import ToolStateFlattener


class StepParsingStrategy(ABC):
    step: dict[str, Any]

    @abstractmethod
    def parse(self, step: dict[str, Any])  -> WorkflowStep:
        """parses galaxy step in json format to GalaxyWorkflowStep"""
        ...

    @abstractmethod
    def get_step_inputs(self) -> StepInputRegister:
        """creates inputs for this step"""
        ...
    
    @abstractmethod
    def get_step_outputs(self) -> StepOutputRegister:
        """creates outputs for this step"""
        ...




class ToolStepParsingStrategy(StepParsingStrategy):
    def __init__(self) -> None:
        self.inputs: dict[str, StepInput] = {}
        self.flattened_tool_state: dict[str, Any] = {}

    def parse(self, step: dict[str, Any]) -> ToolStep:
        self.gxstep = step
        return ToolStep(
            metadata=self.get_step_metadata(),
            input_register=self.get_step_inputs(),
            output_register=self.get_step_outputs()
        )

    def get_step_metadata(self) -> ToolStepMetadata:
        return init_toolstep_metadata(self.gxstep)

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
