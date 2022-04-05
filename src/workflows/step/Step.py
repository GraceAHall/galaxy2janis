

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple
from datatypes.JanisDatatype import JanisDatatype
from tool.Tool import Tool
from workflows.step.inputs.StepInput import StepInput
from workflows.step.metadata.StepMetadata import InputDataStepMetadata, StepMetadata, ToolStepMetadata
from workflows.step.inputs.StepInputRegister import StepInputRegister
from workflows.step.outputs.StepOutput import StepOutput
from workflows.step.outputs.StepOutputRegister import StepOutputRegister
from workflows.step.values.InputValue import InputValue
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

    def get_uuid(self) -> str:
        return self.metadata.uuid

    @abstractmethod
    def get_docstring(self) -> Optional[str]:
        ...

    def get_input(self, query_name: str) -> Optional[StepInput]:
        return self.input_register.get(query_name)
    
    def list_inputs(self) -> list[StepInput]:
        return self.input_register.list_inputs()
    
    def get_output(self, query_name: str) -> StepOutput:
        return self.output_register.get(query_name)
    
    def list_outputs(self) -> list[StepOutput]:
        return self.output_register.list_outputs()



@dataclass
class InputDataStep(GalaxyWorkflowStep):
    """represents a galaxy input data step"""
    metadata: InputDataStepMetadata
    is_optional: bool=False
    is_collection: bool=False
    collection_type: Optional[str]=None # check this doesnt do weird stuff

    def set_janis_datatypes(self, datatypes: list[JanisDatatype]) -> None:
        self.metadata.janis_datatypes = datatypes

    def get_janis_datatype_str(self) -> str:
        if self.is_collection:
            return f'Array(File)'
        return 'File'

    def get_docstring(self) -> Optional[str]:
        return self.metadata.label

    def __repr__(self) -> str:
        return f'(InputDataStep) step{self.metadata.step_id} - ' + ', '.join([inp.name for inp in self.list_inputs()])


@dataclass
class ToolStep(GalaxyWorkflowStep):
    """represents a galaxy tool step"""
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

    def list_tool_values(self) -> list[Tuple[str, InputValue]]:
        return self.values.list_values()
    
    def get_tool_tags_values(self) -> dict[str, InputValue]:
        out: dict[str, InputValue] = {}
        for uuid, input_value in self.list_tool_values():
            assert(self.tool)
            component_tag = self.tool.tag_manager.get('tool_input', uuid)
            out[component_tag] = input_value
        return out
    
    def get_unlinked_values(self, only_connections: bool=True) -> list[str]:
        return [x.value for x in self.values.list_unlinked()]

    def get_docstring(self) -> Optional[str]:
        return self.metadata.label

    def get_uri(self) -> str:
        return self.metadata.get_uri()
    
    def __repr__(self) -> str:
        return f'(ToolStep) step{self.metadata.step_id} - {self.get_tool_name()}'
