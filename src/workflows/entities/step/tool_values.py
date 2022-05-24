


from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple
from xmltool.param.Param import Param


class InputValueType(Enum):
    RUNTIME         = auto()
    ENV_VAR         = auto()
    STRING          = auto()
    NUMERIC         = auto()
    BOOLEAN         = auto()
    NONE            = auto()


@dataclass
class InputValue(ABC):
    comptype: str # this should really be an enum
    gxparam: Optional[Param]

    def __post_init__(self):
        self.is_default_value: bool = False
        self.linked: bool = False

    @property
    def abstract_value(self) -> str:
        if isinstance(self, StaticInputValue) or isinstance(self, DefaultInputValue):
            return str(self.value)
        elif isinstance(self, ConnectionInputValue):
            return f'step {self.step_id} {self.step_output}'
        else:
            return 'uuid'


@dataclass
class ConnectionInputValue(InputValue):
    step_id: int
    step_output: str 


@dataclass
class WorkflowInputInputValue(InputValue):
    input_uuid: str
    is_runtime: bool = False


@dataclass
class StaticInputValue(InputValue):
    value: str
    valtype: InputValueType


@dataclass
class DefaultInputValue(InputValue):
    value: str
    valtype: InputValueType


@dataclass
class RuntimeInputValue(InputValue):
    """
    RuntimeInputValues are eventually migrated to WorkflowInputInputValues.
    This is a temporary class and will never be present in a finalised workflow. ?
    """
    pass


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



