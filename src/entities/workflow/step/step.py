

from __future__ import annotations
from typing import Optional

from entities.tool import Tool

# this module imports
from ..registers.StepInputRegister import StepInputRegister
from ..registers.StepOutputRegister import StepOutputRegister
from .metadata import StepMetadata


class WorkflowStep:
    """represents a galaxy tool step"""

    def __init__(self, metadata: StepMetadata):
        self.metadata = metadata
        self.inputs: StepInputRegister = StepInputRegister()
        self.outputs: StepOutputRegister = StepOutputRegister()
        self._tool: Optional[Tool] = None

    @property
    def tool(self) -> Tool:
        if self._tool:
            return self._tool
        raise RuntimeError()

    def set_tool(self, tool: Tool) -> None:
        self._tool = tool

    @property
    def tool_name(self) -> str:
        return self.metadata.wrapper.tool_id

    @property
    def uuid(self) -> str:
        return self.metadata.uuid  # why?
    
    @property
    def docstring(self) -> Optional[str]:
        return self.metadata.label

    def __repr__(self) -> str:
        return f'(WorkflowStep) step{self.metadata.step_id} - {self.tool_name}'
