







from typing import Any, Optional
from tool.Tool import Tool
from workflows.step.inputs.StepInput import ConnectionStepInput, RuntimeStepInput, StaticStepInput, StepInput

"""
"input_connections": {
    "input_file": {
        "id": 1,
        "output_name": "output"
    }
},
"tool_state": {
    "adapters": {
        "__class__": "RuntimeValue"
    }, 
    "contaminants": {
        "__class__": "RuntimeValue"
    }, 
    "input_file": {
        "__class__": "ConnectedValue"
    }, 
    "kmers": "7", 
    "limits": {
        "__class__": "RuntimeValue"
    }, 
    "min_length": null, 
    "nogroup": "false", 
    "__page__": null, 
    "__rerun_remap_job_id__": null
}
"""



class StepInputRegister:
    """
    holds the data above
    galaxy varnames are linked to actual Param objects
    allows getting the value of an input by supplying a galaxy varname
    """
    def __init__(self, step_inputs: list[StepInput]):
        self.register = step_inputs

    def get(self, gxvarname: str) -> Optional[StepInput]:
        for inp in self.register:
            if inp.gxvarname == gxvarname:
                return inp
        return None
    
    def list(self) -> list[StepInput]:
        return self.register

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        static_inputs = [inp for inp in self.list() if isinstance(inp, StaticStepInput)]
        for inp in static_inputs:
            out[inp.gxvarname] = inp.value
        return out

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

