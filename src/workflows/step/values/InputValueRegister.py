



from typing import Optional, Tuple
from workflows.step.values.InputValue import InputValue, WorkflowInputInputValue


class InputValueRegister:
    def __init__(self):
        self.linked_values: dict[str, InputValue] = {}
        self.unlinked_values: list[InputValue] = []

    @property
    def linked(self) -> list[Tuple[str, InputValue]]:
        return list(self.linked_values.items())
    
    @property
    def unlinked(self) -> list[InputValue]:
        return self.unlinked_values
    
    @property
    def runtime(self) -> list[WorkflowInputInputValue]:
        values = [value for _, value in self.linked if isinstance(value, WorkflowInputInputValue)]
        values = [value for value in values if value.is_runtime]
        return values

    def get(self, uuid: str) -> Optional[InputValue]:
        if uuid in self.linked_values:
            return self.linked_values[uuid]

    def update_linked(self, uuid: str, value: InputValue) -> None:
        value.linked = True
        self.linked_values[uuid] = value
    
    def update_unlinked(self, value: InputValue) -> None:
        value.linked = False
        self.unlinked_values.append(value)
    
    def __str__(self) -> str:
        out: str = '\nInputValueRegister -----\n'
        out += f"{'[gxparam]':30}{'[input type]':30}{'[value]':30}\n"
        for inp in self.linked_values.values():
            param_name = inp.gxparam.name if inp.gxparam else 'none'
            out += f'{param_name:30}{str(type(inp).__name__):30}{inp.abstract_value:30}\n'
        return out



