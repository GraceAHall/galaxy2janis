


from dataclasses import dataclass, field
from typing import Optional
from command.components.CommandComponent import CommandComponent
from datatypes import JanisDatatype


@dataclass
class StepOutput:
    gx_varname: str
    gx_datatypes: list[str]
    is_wflow_out: bool
    janis_datatypes: list[JanisDatatype] = field(default_factory=list)
    tool_output: Optional[CommandComponent] = None


class StepOutputRegister:
    def __init__(self, step_outputs: list[StepOutput]):
        self.register = step_outputs

    def get(self, gxvarname: str) -> StepOutput:
        for output in self.register:
            if output.gx_varname == gxvarname:
                return output
        raise RuntimeError(f'could not find output {gxvarname}')

    def list(self) -> list[StepOutput]:
        return self.register


