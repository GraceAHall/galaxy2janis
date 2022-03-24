


from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Optional, Tuple

from .Step import GalaxyWorkflowStep, InputDataStep, ToolStep
from .StepInput import StepInput, init_connection_step_input, init_static_step_input, init_userdefined_step_input
from .StepOutput import StepOutput, init_step_output
from .StepMetadata import (
    ToolStepMetadata,
    init_inputdatastep_metadata, 
    init_toolstep_metadata
)



class StepParsingStrategy(ABC):
    step: dict[str, Any]

    @abstractmethod
    def parse(self, step: dict[str, Any])  -> GalaxyWorkflowStep:
        """parses galaxy step in json format to GalaxyWorkflowStep"""
        ...

    @abstractmethod
    def get_step_inputs(self) -> list[StepInput]:
        """creates inputs for this step"""
        ...
    
    @abstractmethod
    def get_step_outputs(self) -> list[StepOutput]:
        """creates outputs for this step"""
        ...


class InputDataStepParsingStrategy(StepParsingStrategy):

    def parse(self, step: dict[str, Any])  -> InputDataStep:
        self.step = step
        return InputDataStep(
            metadata=init_inputdatastep_metadata(self.step),
            inputs=self.get_step_inputs(),
            outputs=self.get_step_outputs(),
            optional=step['tool_state']['optional'], # TODO check this!
            is_collection=self.is_collection(),
            collection_type=self.get_collection_type()
        )

    def get_step_inputs(self) -> list[StepInput]:
        return [init_userdefined_step_input(inp) for inp in self.step['inputs']]
    
    def get_step_outputs(self) -> list[StepOutput]:
        return [init_step_output(self.step, {'name': 'output', 'type': 'File'})]

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

    def parse(self, step: dict[str, Any])  -> ToolStep:
        self.step = step
        return ToolStep(
            metadata=self.get_step_metadata(),
            inputs=self.get_step_inputs(),
            outputs=self.get_step_outputs()
        )

    def get_step_metadata(self) -> ToolStepMetadata:
        return init_toolstep_metadata(self.step)

    def get_step_inputs(self) -> list[StepInput]:
        self.inputs = {}
        self.parse_connection_inputs()
        self.parse_user_defined_inputs()
        self.parse_static_inputs()
        return list(self.inputs.values())

    def parse_connection_inputs(self) -> None:
        for name, details in self.step['input_connections'].items():
            self.inputs[name] = init_connection_step_input(name, details)

    def parse_user_defined_inputs(self) -> None:
        for details in self.step['inputs']:
            self.inputs[details['name']] = init_userdefined_step_input(details)

    def parse_static_inputs(self) -> None:
        self.set_flattened_tool_state()
        for name, value in self.flattened_tool_state.items():
            if not name.endswith('__') and name not in self.inputs:
                self.inputs[name] = init_static_step_input(name, value)

    def set_flattened_tool_state(self) -> None:
        for name, value in self.step['tool_state'].items():
            self.explore_node(name, value, [])

    def explore_node(self, name: str, value: Any, path: list[str]) -> Any:
        path_copy = deepcopy(path)
        if value == {"__class__": "RuntimeValue"}:
            self.add_to_flattened_tool_state(name, 'RuntimeValue', path_copy)
        elif isinstance(value, dict):
            path_copy.append(name)
            for key, val in value.items():
                self.explore_node(key, val, path_copy)
        else:
            self.add_to_flattened_tool_state(name, value, path_copy)
    
    def add_to_flattened_tool_state(self, name: str, value: Any, path_copy: list[str]) -> None:
        if len(path_copy) > 0:
            full_name = f'{".".join(path_copy)}.{name}'
        else:
            full_name = name
        self.flattened_tool_state[full_name] = value
        

    def get_step_outputs(self) -> list[StepOutput]:
        return [init_step_output(self.step, out) for out in self.step['outputs']]



