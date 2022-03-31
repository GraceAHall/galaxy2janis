


from abc import ABC, abstractmethod

from typing import Any, Optional

from workflows.step.Step import GalaxyWorkflowStep, InputDataStep, ToolStep
from workflows.step.inputs.StepInput import StepInput, init_connection_step_input, init_static_step_input, init_userdefined_step_input
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
    def parse(self, step: dict[str, Any])  -> GalaxyWorkflowStep:
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


class InputDataStepParsingStrategy(StepParsingStrategy):

    def parse(self, step: dict[str, Any])  -> InputDataStep:
        self.step = step
        return InputDataStep(
            metadata=init_inputdatastep_metadata(self.step),
            input_register=self.get_step_inputs(),
            output_register=self.get_step_outputs(),
            optional=step['tool_state']['optional'], # TODO check this!
            is_collection=self.is_collection(),
            collection_type=self.get_collection_type()
        )

    def get_step_inputs(self) -> StepInputRegister:
        step_inputs = [init_userdefined_step_input(inp) for inp in self.step['inputs']]
        return StepInputRegister(step_inputs)
    
    def get_step_outputs(self) -> StepOutputRegister:
        step_outputs = [init_input_step_output(self.step)]
        return StepOutputRegister(step_outputs)

    def is_collection(self) -> bool:
        if self.step['type'] == 'data_collection_input':
            return True
        return False
    
    def get_collection_type(self) -> Optional[str]:
        if self.step['type'] == 'data_collection_input':
            return self.step['tool_state']['collection_type']
        return None



class ToolStepParsingStrategy(StepParsingStrategy):
    def __init__(self) -> None:
        self.inputs: dict[str, StepInput] = {}
        self.flattened_tool_state: dict[str, Any] = {}

    def parse(self, step: dict[str, Any]) -> ToolStep:
        self.step = step
        return ToolStep(
            metadata=self.get_step_metadata(),
            input_register=self.get_step_inputs(),
            output_register=self.get_step_outputs()
        )

    def get_step_metadata(self) -> ToolStepMetadata:
        return init_toolstep_metadata(self.step)

    def get_step_inputs(self) -> StepInputRegister:
        self.inputs = {}
        self.set_flattened_tool_state()
        self.parse_connection_inputs()
        self.parse_user_defined_inputs()
        self.parse_static_inputs()
        step_inputs = list(self.inputs.values())
        return StepInputRegister(step_inputs) 

    def set_flattened_tool_state(self) -> None:
        flattener = ToolStateFlattener()
        self.flattened_tool_state = flattener.flatten(self.step)

    def parse_connection_inputs(self) -> None:
        for name, details in self.step['input_connections'].items():
            self.inputs[name] = init_connection_step_input(name, details)

    def parse_user_defined_inputs(self) -> None:
        for details in self.step['inputs']:
            self.inputs[details['name']] = init_userdefined_step_input(details)

    def parse_static_inputs(self) -> None:
        for name, value in self.flattened_tool_state.items():
            if not name.endswith('__') and name not in self.inputs:
                self.inputs[name] = init_static_step_input(name, value)

    def get_step_outputs(self) -> StepOutputRegister:
        step_outputs = [init_tool_step_output(self.step, out) for out in self.step['outputs']]
        return StepOutputRegister(step_outputs)



