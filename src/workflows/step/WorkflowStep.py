

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple

from tool.Tool import Tool
from workflows.step.inputs.StepInput import StepInput
from workflows.step.metadata.StepMetadata import StepMetadata
from workflows.step.inputs.StepInputRegister import StepInputRegister
from workflows.step.outputs.StepOutput import StepOutput
from workflows.step.outputs.StepOutputRegister import StepOutputRegister
from workflows.step.values.InputValue import InputValue, WorkflowInputInputValue
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


@dataclass
class WorkflowStep:
    """represents a galaxy tool step"""
    metadata: StepMetadata
    input_register: StepInputRegister
    output_register: StepOutputRegister
    tool: Optional[Tool] = None
    values: InputValueRegister = InputValueRegister()

    def get_uuid(self) -> str:
        return self.metadata.uuid

    def get_input(self, query_name: str) -> Optional[StepInput]:
        return self.input_register.get(query_name)
    
    def list_inputs(self) -> list[StepInput]:
        return self.input_register.list_inputs()
    
    def get_output(self, query_name: str) -> StepOutput:
        return self.output_register.get(query_name)
    
    def list_outputs(self) -> list[StepOutput]:
        return self.output_register.list_outputs()

    def set_definition_path(self, path: str) -> None:
        self.metadata.tool_definition_path = path
    
    def get_definition_path(self) -> str:
        if self.metadata.tool_definition_path:
            return self.metadata.tool_definition_path
        raise RuntimeError('tool_definition_path not set for tool step')

    def get_tool_name(self) -> str:
        return self.metadata.tool_id

    def list_linked_values(self) -> list[Tuple[str, InputValue]]:
        return self.values.list_linked()
    
    def list_unlinked_values(self) -> list[InputValue]:
        return self.values.list_unlinked()
    
    def list_runtime_values(self) -> list[WorkflowInputInputValue]:
        linked_values = self.list_linked_values()
        runtime_inputs = [value for _, value in linked_values if isinstance(value, WorkflowInputInputValue)]
        return runtime_inputs

    def get_tool_tags_values(self) -> list[Tuple[str, InputValue]]:
        """translates [uuid, value] into [tag, value] for tool input values"""
        out: list[Tuple[str, InputValue]] = []
        for uuid, input_value in self.list_linked_values():
            assert(self.tool)
            component_tag = self.tool.tag_manager.get(uuid)
            out.append((component_tag, input_value))
        return out

    def get_docstring(self) -> Optional[str]:
        return self.metadata.label

    def get_uri(self) -> str:
        return self.metadata.get_uri()
    
    def __repr__(self) -> str:
        return f'(WorkflowStep) step{self.metadata.step_id} - {self.get_tool_name()}'
