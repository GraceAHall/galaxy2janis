


from dataclasses import dataclass
from typing import Optional
from shellparser.components.CommandComponent import CommandComponent


@dataclass
class StepOutput:
    gx_varname: str
    gx_datatypes: list[str]
    is_wflow_out: bool
    tool_output: Optional[CommandComponent] = None


