


from dataclasses import dataclass
from uuid import uuid4

from datatypes.JanisDatatype import JanisDatatype
from gx.command.components import OutputComponent


@dataclass
class StepOutput:
    step_uuid: str
    janis_datatypes: list[JanisDatatype]
    is_wflow_out: bool
    tool_output: OutputComponent

    def __post_init__(self):
        self.uuid = str(uuid4())


