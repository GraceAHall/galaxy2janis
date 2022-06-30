



from typing import Any, Optional
from ..step.inputs import StepInput, StaticStepInput


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
