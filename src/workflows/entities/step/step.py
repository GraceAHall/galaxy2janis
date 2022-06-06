

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple

from tool.Tool import Tool
from .metadata import StepMetadata
from .inputs import StepInputRegister
from .outputs import StepOutputRegister
from .tool_values import InputValue, InputValueRegister


@dataclass
class WorkflowStep:
    """represents a galaxy tool step"""
    metadata: StepMetadata
    inputs: StepInputRegister
    outputs: StepOutputRegister
    tool: Tool

    def __post_init__(self):
        self.tool_values: InputValueRegister = InputValueRegister()

    @property
    def uuid(self) -> str:
        return self.metadata.uuid  # why?
    
    @property
    def docstring(self) -> Optional[str]:
        return self.metadata.label

    @property
    def tool_name(self) -> str:
        return self.metadata.wrapper.tool_id

    def get_tool_tags_values(self) -> list[Tuple[str, InputValue]]:
        """translates [uuid, value] into [tag, value] for tool input values"""
        out: list[Tuple[str, InputValue]] = []
        for uuid, input_value in self.tool_values.linked:
            component_tag = self.tool.tag_manager.get(uuid)
            out.append((component_tag, input_value))
        return out


    def __repr__(self) -> str:
        return f'(WorkflowStep) step{self.metadata.step_id} - {self.tool_name}'
