

from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

from datatypes.JanisDatatype import JanisDatatype


@dataclass
class WorkflowInput:
    name: str
    step_id: int
    step_tag: Optional[str]
    array: bool
    optional: bool = False
    is_galaxy_input_step: bool = False
    gx_datatypes: list[str] = field(default_factory=list)
    janis_datatypes: list[JanisDatatype] = field(default_factory=list)

    def __post_init__(self):
        self.uuid: str = str(uuid4())

    @property
    def docstring(self) -> Optional[str]:
        return 'None yet!'
        

