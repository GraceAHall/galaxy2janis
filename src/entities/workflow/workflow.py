

from typing import Optional
from uuid import uuid4

from .step.step import WorkflowStep
from .metadata import WorkflowMetadata
from .output import WorkflowOutput
from .input import WorkflowInput
import tags


class Workflow:
    """
    a Workflow() is the final representation of the galaxy workflow
    being parsed. Includes workflow metadata, inputs, tool steps, and outputs. 
    step_ids are used to lookup key information. 
    each input, step, and output is stored with step_id as key. 
    that way everything can be referenced properly. 
    """
    def __init__(self):
        self.inputs: list[WorkflowInput] = []
        self.steps: dict[int, WorkflowStep] = {}
        self.outputs: list[WorkflowOutput] = []
        self.uuid: str = str(uuid4())
        self._metadata: Optional[WorkflowMetadata] = None
        tags.workflow.register(self)

    @property
    def metadata(self) -> WorkflowMetadata:
        if self._metadata:
            return self._metadata
        raise RuntimeError('no metadata set')

    def set_metadata(self, metadata: WorkflowMetadata) -> None:
        self._metadata = metadata

    def add_step(self, step: WorkflowStep) -> None:
        self.steps[step.metadata.step_id] = step
        tags.workflow.register(step)
    
    def add_input(self, w_inp: WorkflowInput) -> None:
        self.inputs.append(w_inp)
        tags.workflow.register(w_inp)
    
    def add_output(self, w_out: WorkflowOutput) -> None:
        self.outputs.append(w_out)
        tags.workflow.register(w_out)

    def get_input(self, step_id: Optional[int]=None, input_uuid: Optional[str]=None) -> Optional[WorkflowInput]:
        if step_id is not None:
            relevant_inputs = [x for x in self.inputs if x.step_id == step_id]
            if relevant_inputs:
                return relevant_inputs[0]
        elif input_uuid is not None:
            relevant_inputs = [x for x in self.inputs if x.uuid == input_uuid]
            if relevant_inputs:
                return relevant_inputs[0]
        else:
            raise RuntimeError('get_input needs to be supplied either step_id or input_uuid')

    def get_step_by_step_id(self, step_id: int) -> WorkflowStep:
        return self.steps[step_id]

    def get_step_tag_by_step_id(self, step_id: int) -> str:
        """uuids provide access to identifier tags"""
        step_uuid = self.steps[step_id].uuid
        return tags.workflow.get(step_uuid)

    def list_steps(self) -> list[WorkflowStep]:
        the_list = list(self.steps.values())
        the_list.sort(key=lambda x: x.metadata.step_id)
        return the_list

    def get_tool_steps_tags(self) -> dict[str, WorkflowStep]:
        """used near end of runtime once tags are stable"""
        out: dict[str, WorkflowStep] = {}
        for step in self.list_steps():
            tag = tags.workflow.get(step.uuid)
            out[tag] = step
        return out

    def get_inputs_tags(self) -> dict[str, WorkflowInput]:
        """used near end of runtime once tags are stable"""
        out: dict[str, WorkflowInput] = {}
        for w_input in self.inputs:
            tag = tags.workflow.get(w_input.uuid)
            out[tag] = w_input
        return out
    
    def get_outputs_tags(self) -> dict[str, WorkflowOutput]:
        out: dict[str, WorkflowOutput] = {}
        for w_output in self.outputs:
            tag = tags.workflow.get(w_output.uuid)
            out[tag] = w_output
        return out
    


    

