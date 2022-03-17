


from abc import ABC
from dataclasses import dataclass
from typing import Optional
from .StepMetadata import StepMetadata
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
class WorkflowStep(ABC):
    metadata: StepMetadata
    inputs: list[StepInput]
    outputs: list[StepOutput]

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
class InputDataStep(WorkflowStep):
    optional: bool
    is_collection: bool
    collection_type: Optional[str]

    def __repr__(self) -> str:
        return f'(InputDataStep) step{self.metadata.step_id} - ' + ', '.join([inp.name for inp in self.inputs])

@dataclass
class ToolStep(WorkflowStep):
    # scatter?

    def get_uri(self) -> str:
        return self.metadata.get_uri()
    
    def get_tool_name(self) -> str:
        return self.metadata.tool_name

    def __repr__(self) -> str:
        return f'(ToolStep) step{self.metadata.step_id} - {self.get_tool_name()}'
