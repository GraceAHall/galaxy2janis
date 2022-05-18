

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple

from tool.Tool import Tool
from workflows.step.metadata.StepMetadata import StepMetadata
from workflows.step.inputs.StepInputRegister import StepInputRegister
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


@dataclass
class WorkflowStep:
    """represents a galaxy tool step"""
    metadata: StepMetadata
    inputs: StepInputRegister
    outputs: StepOutputRegister
    tool: Tool

    def __post_init__(self):
        self.tool_values: InputValueRegister = InputValueRegister()

    def get_uuid(self) -> str:
        return self.metadata.uuid

    def set_tool_definition_path(self, path: str) -> None:
        self.metadata.tool_definition_path = path
    
    def get_tool_definition_path(self) -> str:
        if self.metadata.tool_definition_path:
            return self.metadata.tool_definition_path
        raise RuntimeError()

    def set_step_definition_path(self, folder: str) -> None:
        raise NotImplementedError()
    
    def get_step_definition_path(self) -> str:
        raise NotImplementedError()

    def get_tool_name(self) -> str:
        return self.metadata.tool_id

    def get_tool_tags_values(self) -> list[Tuple[str, InputValue]]:
        """translates [uuid, value] into [tag, value] for tool input values"""
        out: list[Tuple[str, InputValue]] = []
        for uuid, input_value in self.tool_values.linked:
            component_tag = self.tool.tag_manager.get(uuid)
            out.append((component_tag, input_value))
        return out

    def get_docstring(self) -> Optional[str]:
        return self.metadata.label

    def __repr__(self) -> str:
        return f'(WorkflowStep) step{self.metadata.step_id} - {self.get_tool_name()}'
