


from dataclasses import dataclass
from uuid import uuid4
from datatypes.JanisDatatype import JanisDatatype
from shellparser.components.CommandComponent import CommandComponent


@dataclass
class StepOutput:
    janis_datatypes: list[JanisDatatype]
    is_wflow_out: bool
    tool_output: CommandComponent

    def __post_init__(self):
        self.uuid = str(uuid4())


