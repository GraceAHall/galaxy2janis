

from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from datatypes.JanisDatatype import JanisDatatype


@dataclass
class WorkflowInput:
    name: str
    array: bool
    optional: bool
    is_runtime: bool
    datatype: JanisDatatype

    def __post_init__(self):
        self.uuid: str = str(uuid4())

    @property
    def docstring(self) -> Optional[str]:
        return 'None yet!'
        

