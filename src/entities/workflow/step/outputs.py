


from dataclasses import dataclass, field
from typing import Optional
from shellparser.components.CommandComponent import CommandComponent
from datatypes import JanisDatatype


@dataclass
class StepOutput:
    gx_varname: str
    gx_datatypes: list[str]
    is_wflow_out: bool
    janis_datatypes: list[JanisDatatype] = field(default_factory=list)
    tool_output: Optional[CommandComponent] = None


