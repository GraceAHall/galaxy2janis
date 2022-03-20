

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from tool.Tool import Tool
from .StepMetadata import InputDataStepMetadata, StepMetadata, ToolStepMetadata
from .StepInput import StepInput
from .StepOutput import StepOutput


"""
JANIS
Workflow.step(
    identifier: str, 
    tool: janis_core.tool.tool.Tool, 
    scatter: Union[str, List[str], ScatterDescription] = None, 
)
eg 
w.step(
    "bwamem",   # identifier
    BwaMemLatest(
        reads=w.fastq,
        readGroupHeaderLine=w.read_group,
        reference=w.reference
    )
)
"""


### step types 
@dataclass
class GalaxyWorkflowStep(ABC):
    metadata: StepMetadata
    inputs: list[StepInput]
    outputs: list[StepOutput]

    @abstractmethod
    def generate_workflow_step(self) -> str:
        ...

    def get_output(self, query_name: str) -> StepOutput:
        for output in self.outputs:
            if output.name == query_name:
                return output
        raise RuntimeError(f'could not find output {query_name}')
    
    def get_input(self, query_name: str) -> StepInput:
        for inp in self.inputs:
            if inp.name == query_name:
                return inp
        raise RuntimeError(f'could not find output {query_name}')

@dataclass
class InputDataStep(GalaxyWorkflowStep):
    metadata: InputDataStepMetadata
    optional: bool
    is_collection: bool
    collection_type: Optional[str]

    def generate_workflow_step(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'(InputDataStep) step{self.metadata.step_id} - ' + ', '.join([inp.name for inp in self.inputs])


class ToolStep(GalaxyWorkflowStep):
    metadata: ToolStepMetadata
    tool: Optional[Tool] = None
    # scatter?

    def get_uri(self) -> str:
        return self.metadata.get_uri()
    
    def get_tool_name(self) -> str:
        return self.metadata.tool_name
    
    def generate_workflow_step(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'(ToolStep) step{self.metadata.step_id} - {self.get_tool_name()}'
