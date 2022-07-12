

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
        self.uuid: str = str(uuid4())
        self.inputs: list[WorkflowInput] = []
        self.outputs: list[WorkflowOutput] = []
        self._steps: list[WorkflowStep] = []
        self._metadata: Optional[WorkflowMetadata] = None
    
    @property
    def steps(self) -> list[WorkflowStep]:
        the_list = self._steps
        the_list.sort(key=lambda x: x.metadata.step_id)
        return the_list

    @property
    def metadata(self) -> WorkflowMetadata:
        if self._metadata:
            return self._metadata
        raise RuntimeError('no metadata set')

    def set_metadata(self, metadata: WorkflowMetadata) -> None:
        self._metadata = metadata
        tags.workflow.register(self)
    
    def add_input(self, w_inp: WorkflowInput) -> None:
        tags.workflow.register(w_inp)
        self.inputs.append(w_inp)

    def add_step(self, step: WorkflowStep) -> None:
        tags.workflow.register(step)
        self.steps.append(step)
    
    def add_output(self, w_out: WorkflowOutput) -> None:
        tags.workflow.register(w_out)
        self.outputs.append(w_out)

    def get_input(self, query_uuid: str) -> WorkflowInput:
        for winp in self.inputs:
            if winp.uuid == query_uuid:
                return winp
        raise RuntimeError('could not find input with uuid')

