







from typing import Optional
from tool.Tool import Tool
from workflows.step.inputs.StepInput import ConnectionStepInput, RuntimeStepInput, StaticStepInput, StepInput


class StepInputRegister:
    def __init__(self, step_inputs: list[StepInput]):
        self.register = step_inputs

    def get(self, query_name: str) -> Optional[StepInput]:
        for inp in self.register:
            if inp.name == query_name:
                return inp
        return None

    def get_connection(self, query_name: str) -> Optional[StepInput]:
        step_input = self.get(query_name)
        if isinstance(step_input, ConnectionStepInput):
            return step_input
        return None
    
    def get_runtime(self, query_name: str) -> Optional[StepInput]:
        step_input = self.get(query_name)
        if isinstance(step_input, RuntimeStepInput):
            return step_input
        return None

    def get_static(self, query_name: str) -> Optional[StepInput]:
        step_input = self.get(query_name)
        if isinstance(step_input, StaticStepInput):
            return step_input
        return None

    def list_inputs(self) -> list[StepInput]:
        return self.register

    def assign_gxparams(self, tool: Tool) -> None:
        for step_input in self.register:
            gxparam = tool.get_gxparam(step_input.name)
            step_input.gxparam = gxparam


