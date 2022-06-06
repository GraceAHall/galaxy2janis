
from dataclasses import dataclass
from typing import Any, Optional

from galaxy_wrappers.wrappers.Wrapper import Wrapper


@dataclass
class StepMetadata:
    wrapper: Wrapper
    uuid: str
    step_id: int
    step_name: str
    tool_state: dict[str, Any]
    workflow_outputs: list[dict[str, Any]]
    label: Optional[str] = None

    @property
    def tool_definition_path(self) -> str:
        return f'tools/{self.wrapper.tool_id}/{self.wrapper.tool_id}.py'
    
    @property
    def step_definition_path(self) -> str:
        raise NotImplementedError()
        return f'{self.wrapper.tool_id}/{self.wrapper.tool_id}.py'

    
    





        



