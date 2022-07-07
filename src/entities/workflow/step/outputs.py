


from dataclasses import dataclass
from typing import Optional
from datatypes.JanisDatatype import JanisDatatype
from shellparser.components.CommandComponent import CommandComponent


@dataclass
class StepOutput:
    gx_varname: str
    janis_datatypes: list[JanisDatatype]
    is_wflow_out: bool
    tool_output: Optional[CommandComponent] = None


