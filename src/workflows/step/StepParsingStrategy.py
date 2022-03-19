


from abc import ABC, abstractmethod
from typing import Any, Optional

from .Step import GalaxyWorkflowStep, InputDataStep, ToolStep
from .StepInput import StepInput, init_connection_step_input, init_static_step_input, init_userdefined_step_input
from .StepOutput import StepOutput, init_step_output
from .StepMetadata import init_inputdatastep_metadata, init_toolstep_metadata




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

    def parse(self, step: dict[str, Any])  -> ToolStep:
        self.step = step
        return ToolStep(
            metadata=init_toolstep_metadata(self.step),
            inputs=self.get_step_inputs(),
            outputs=self.get_step_outputs()
        )

    def get_step_inputs(self) -> list[StepInput]:
        inputs: list[StepInput] = []
        parsed_input_names: set[str] = set()
        # connections
        for name, details in self.step['input_connections'].items():
            inputs.append(init_connection_step_input(name, details))
            parsed_input_names.add(name)
        # user defined
        for details in self.step['inputs']:
            inputs.append(init_userdefined_step_input(details))
            parsed_input_names.add(details['name'])
        # static tool state
        for name, value in self.step['tool_state'].items():
            if not name.startswith('__') and name not in parsed_input_names:
                inputs.append(init_static_step_input(name, value))
        return inputs
    
    def get_step_outputs(self) -> list[StepOutput]:
        return [init_step_output(self.step, out) for out in self.step['outputs']]



