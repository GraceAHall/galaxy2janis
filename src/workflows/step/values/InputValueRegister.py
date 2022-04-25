



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

    def get_linked(self, uuid: str) -> Optional[InputValue]:
        if uuid in self.linked_values:
            return self.linked_values[uuid]

    def update_linked(self, uuid: str, value: InputValue) -> None:
        value.linked = True
        self.linked_values[uuid] = value
    
    def update_unlinked(self, value: InputValue) -> None:
        value.linked = False
        self.unlinked_values.append(value)
    
    def __str__(self) -> str:
        out_str: str = '\nInputValueRegister -----\n'
        out_str += f'{"[uuid]":>20}{"[value]":>20}{"[type]":>40}\n'
        # for uuid, input_value in self.values.items():
        #     out_str += f'{uuid:>20}{input_value.value:>20}{input_value.valtype:>40}\n'
        return out_str

