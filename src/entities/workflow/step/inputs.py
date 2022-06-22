



from abc import ABC
from dataclasses import dataclass
from typing import Any, Optional
from gx.xmltool.param.Param import Param
from entities.tool.Tool import Tool


@dataclass
class StepInput(ABC):
    gxvarname: str

    def __post_init__(self):
        self.linked: bool = False
        self.gxparam: Optional[Param] = None


@dataclass
class WorkflowInputStepInput(StepInput):
    step_id: int


@dataclass
class ConnectionStepInput(StepInput):
    step_id: int
    output_name: str


@dataclass
class StaticStepInput(StepInput):
    value: str


@dataclass
class RuntimeStepInput(StepInput):
    value: str = 'RuntimeValue'


class StepInputRegister:
    """
    holds the data above. 
    galaxy varnames are linked to actual Param objects.
    allows getting the value of an input by supplying a galaxy varname.
    """
    def __init__(self):
        self.register: list[StepInput] = []

    def add(self, step_input: StepInput) -> None:
        self.register.append(step_input)

    def get(self, gxvarname: str) -> Optional[StepInput]:
        for inp in self.register:
            if inp.gxvarname == gxvarname:
                return inp
        return None
    
    def list(self) -> list[StepInput]:
        return self.register
    
    def to_dict(self) -> dict[str, Any]:
        the_dict: dict[str, Any] = {}
        static_inputs = [inp for inp in self.list() if isinstance(inp, StaticStepInput)]
        for inp in static_inputs:
            self.update_dict(inp, the_dict)
        return the_dict

    def update_dict(self, inp: StaticStepInput, the_dict: dict[str, Any]) -> None:
        name_heirarchy = inp.gxvarname.split('.')
        node = the_dict
        for i, elem in enumerate(name_heirarchy):
            if i < len(name_heirarchy) - 1:
                if elem not in the_dict:
                    node[elem] = {}
                node = node[elem]
            else:
                node[elem] = inp.value

    def get_connection(self, gxvarname: str) -> Optional[StepInput]:
        step_input = self.get(gxvarname)
        if isinstance(step_input, ConnectionStepInput):
            return step_input
        return None
    
    def get_runtime(self, gxvarname: str) -> Optional[StepInput]:
        step_input = self.get(gxvarname)
        if isinstance(step_input, RuntimeStepInput):
            return step_input
        return None

    def get_static(self, gxvarname: str) -> Optional[StepInput]:
        step_input = self.get(gxvarname)
        if isinstance(step_input, StaticStepInput):
            return step_input
        return None

    def assign_gxparams(self, tool: Tool) -> None:
        for step_input in self.register:
            step_input.gxparam = tool.get_gxparam(step_input.gxvarname)
 