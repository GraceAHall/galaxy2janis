

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from entities.tool.Tool import Tool
from ..registers.StepInputRegister import StepInputRegister
from ..registers.StepOutputRegister import StepOutputRegister
from .metadata import StepMetadata
from .tool_values import InputValueRegister


@dataclass
class WorkflowStep:
    """represents a galaxy tool step"""
    metadata: StepMetadata
    tool: Tool
    inputs: StepInputRegister
    outputs: StepOutputRegister

    def __post_init__(self):
        self.tool_values: InputValueRegister = InputValueRegister()

    @property
    def tool_name(self) -> str:
        return self.metadata.wrapper.tool_id

    @property
    def uuid(self) -> str:
        return self.metadata.uuid  # why?
    
    @property
    def docstring(self) -> Optional[str]:
        return self.metadata.label
    
    # def get_tool_tags_values(self) -> list[Tuple[str, InputValue]]:
    #     """translates [uuid, value] into [tag, value] for tool input values"""
    #     out: list[Tuple[str, InputValue]] = []
    #     for uuid, input_value in self.tool_values.linked:
    #         component_tag = self.tool.tag_manager.get(uuid)
    #         out.append((component_tag, input_value))
    #     return out

    def __repr__(self) -> str:
        return f'(WorkflowStep) step{self.metadata.step_id} - {self.tool_name}'
