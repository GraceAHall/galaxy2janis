


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

class InputDataStepParsingStrategy(StepParsingStrategy):

    def parse(self, step: dict[str, Any])  -> InputDataStep:
        self.gxstep = step
        return InputDataStep(
            metadata=init_inputdatastep_metadata(self.gxstep),
            input_register=self.get_step_inputs(),
            output_register=self.get_step_outputs(),
            is_optional=step['tool_state']['optional'], # TODO check this!
            is_collection=self.is_collection(),
            collection_type=self.get_collection_type()
        )

    def get_step_inputs(self) -> StepInputRegister:
        step_inputs = [init_runtime_step_input(inp['name']) for inp in self.gxstep['inputs']]
        return StepInputRegister(step_inputs)
    
    def get_step_outputs(self) -> StepOutputRegister:
        step_outputs = [init_input_step_output(self.gxstep)]
        return StepOutputRegister(step_outputs)

    def is_collection(self) -> bool:
        if self.gxstep['type'] == 'data_collection_input':
            return True
        return False
    
    def get_collection_type(self) -> Optional[str]:
        if self.gxstep['type'] == 'data_collection_input':
            return self.gxstep['tool_state']['collection_type']
        return None
