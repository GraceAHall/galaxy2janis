


from dataclasses import dataclass
from typing import Optional
from uuid import uuid4


@dataclass
class WorkflowOutput:
    step_tag: str
    toolout_tag: str # wtf ???
    gx_datatypes: list[str]

    def __post_init__(self):
        self.uuid: str = str(uuid4())

    @property
    def docstring(self) -> Optional[str]:
        return 'None yet!'






