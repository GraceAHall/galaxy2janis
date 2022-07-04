

from dataclasses import dataclass
from typing import Optional
from uuid import uuid4


@dataclass
class WorkflowInput:
    name: str
    step_id: int
    step_tag: Optional[str]
    gx_datatypes: list[str]
    is_array: bool
    is_galaxy_input_step: bool = False

    def __post_init__(self):
        self.uuid: str = str(uuid4())

    @property
    def docstring(self) -> Optional[str]:
        return 'None yet!'
        

