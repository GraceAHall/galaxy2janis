

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from datatypes.JanisDatatype import JanisDatatype

from tool.Tool import Tool
from workflows.step.inputs.StepInput import StepInput
from workflows.step.metadata.StepMetadata import InputDataStepMetadata, StepMetadata, ToolStepMetadata
from workflows.step.inputs.StepInputRegister import StepInputRegister
from workflows.step.outputs.StepOutput import StepOutput
from workflows.step.outputs.StepOutputRegister import StepOutputRegister
from workflows.step.values.InputValueRegister import InputValueRegister

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
    input_register: StepInputRegister
    output_register: StepOutputRegister

    @abstractmethod
    def get_name(self) -> str:
        """gets the name of this step"""
        ...

    @abstractmethod
    def get_docstring(self) -> Optional[str]:
        ...

    def get_input(self, query_name: str) -> Optional[StepInput]:
        return self.input_register.get(query_name)
    
    def get_output(self, query_name: str) -> Optional[StepOutput]:
        return self.output_register.get(query_name)



@dataclass
class InputDataStep(GalaxyWorkflowStep):
    metadata: InputDataStepMetadata
    optional: bool
    is_collection: bool
    collection_type: Optional[str]=None # check this doesnt do weird stuff

    def get_name(self) -> str:
        return f'{self.metadata.step_name}{self.metadata.step_id}'

    def set_janis_datatypes(self, datatypes: list[JanisDatatype]) -> None:
        self.metadata.janis_datatypes = datatypes

    def get_janis_datatype_str(self) -> str:
        if self.is_collection:
            return f'Array(File)'
        return 'File'

    def get_docstring(self) -> Optional[str]:
        return self.metadata.label

    def __repr__(self) -> str:
        return f'(InputDataStep) step{self.metadata.step_id} - ' + ', '.join([inp.name for inp in self.inputs])


@dataclass
class ToolStep(GalaxyWorkflowStep):
    metadata: ToolStepMetadata
    tool: Optional[Tool] = None
    values: InputValueRegister = InputValueRegister()

    def set_definition_path(self, path: str) -> None:
        self.metadata.tool_definition_path = path
    
    def get_definition_path(self) -> str:
        if self.metadata.tool_definition_path:
            return self.metadata.tool_definition_path
        raise RuntimeError('tool_definition_path not set for tool step')

    def get_tool_name(self) -> str:
        return self.metadata.tool_name

    def get_name(self) -> str:
        return f'step{self.metadata.step_id}_{self.metadata.step_name}'

    def get_docstring(self) -> Optional[str]:
        return self.metadata.label

    def get_uri(self) -> str:
        return self.metadata.get_uri()
    
    def __repr__(self) -> str:
        return f'(ToolStep) step{self.metadata.step_id} - {self.get_tool_name()}'
