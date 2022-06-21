

from dataclasses import dataclass, field
from typing import Optional
from datatypes import JanisDatatype
from datatypes import format_janis_str
from uuid import uuid4


@dataclass
class WorkflowInput:
    name: str
    step_id: int
    step_tag: Optional[str]
    is_array: bool
    is_galaxy_input_step: bool = False
    gx_datatypes: list[str] = field(default_factory=list)
    janis_datatypes: list[JanisDatatype] = field(default_factory=list)

    def __post_init__(self):
        self.uuid: str = str(uuid4())

    @property
    def docstring(self) -> Optional[str]:
        return 'None yet!'
        
    def get_janis_datatype_str(self) -> str:
        return format_janis_str(
            datatypes=self.janis_datatypes,
            is_optional=False,
            is_array=False
        )



