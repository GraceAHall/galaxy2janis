

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Tuple
from datatypes.JanisDatatype import JanisDatatype

from tool.Tool import Tool
from .StepMetadata import InputDataStepMetadata, StepMetadata, ToolStepMetadata
from .StepInput import StepInput
from .StepOutput import StepOutput
from workflows.values.InputValue import InputValue, InputValueType

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
    def get_name(self) -> str:
        """gets the name of this step"""
        ...

    @abstractmethod
    def get_docstring(self) -> Optional[str]:
        ...

    def get_output(self, query_name: str) -> StepOutput:
        for output in self.outputs:
            if output.name == query_name:
                return output
        raise RuntimeError(f'could not find output {query_name}')
    
    def get_input(self, query_name: str) -> Optional[StepInput]:
        for inp in self.inputs:
            if inp.name == query_name:
                return inp
        return None

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
    input_values: dict[str, InputValue] = field(default_factory=dict)

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

    def get_component_type(self, tag: str) -> str:
        if self.tool:
            inp = self.tool.get_input(query_tag=tag)
            if inp:
                return type(inp).__name__.lower()
        raise RuntimeError(f'tool and {tag} input must be known')

    def get_input_values(self) -> dict[str, list[Tuple[str, InputValue]]]:
        out: dict[str, list[Tuple[str, InputValue]]] = {
            'positional': [],
            'flag': [],
            'option': []
        }
        self.populate_input_value_dict(out)
        self.order_input_value_dict(out)
        return out

    def populate_input_value_dict(self, out: dict[str, list[Tuple[str, InputValue]]]) -> None:
        for tag, inputval in self.input_values.items():
            out[self.get_component_type(tag)].append((tag, inputval))

    def order_input_value_dict(self, out: dict[str, list[Tuple[str, InputValue]]]) -> None:
        for component_type, input_values in out.items():
            out[component_type] = self.order_values(input_values)

    def order_values(self, input_values: list[Tuple[str, InputValue]]) -> list[Tuple[str, InputValue]]:
        runtime_inputs = self.get_runtime_input_values(input_values)
        non_runtime_inputs = self.get_nonruntime_input_values(input_values)
        non_runtime_inputs.sort(key=lambda x: x[0])  # sort non runtime inputs alphabetically based on name
        return runtime_inputs + non_runtime_inputs

    def get_runtime_input_values(self, input_values: list[Tuple[str, InputValue]]) -> list[Tuple[str, InputValue]]:
        out: list[Tuple[str, InputValue]] = []
        for tag, inputval in input_values:
            if inputval.valtype == InputValueType.RUNTIME_VALUE:
                out.append((tag, inputval))
        return out
    
    def get_nonruntime_input_values(self, input_values: list[Tuple[str, InputValue]]) -> list[Tuple[str, InputValue]]:
        out: list[Tuple[str, InputValue]] = []
        for tag, inputval in input_values:
            if inputval.valtype != InputValueType.RUNTIME_VALUE:
                out.append((tag, inputval))
        return out

    # deprecated?
    # def get_input_value(self, query: str) -> InputValue:
    #     if query in self.input_values:
    #         return self.input_values[query]
    #     raise RuntimeError()

    def get_uri(self) -> str:
        return self.metadata.get_uri()
    
    def __repr__(self) -> str:
        return f'(ToolStep) step{self.metadata.step_id} - {self.get_tool_name()}'
