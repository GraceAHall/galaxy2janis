


from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from datatypes.JanisDatatype import JanisDatatype


@dataclass
class WorkflowOutput:
    step_uuid: str
    output_uuid: str 
    janis_datatypes: list[JanisDatatype]
    array: bool = False
    optional: bool = False

    def __post_init__(self):
        self.uuid: str = str(uuid4())

    @property
    def docstring(self) -> Optional[str]:
        return 'None yet!'






