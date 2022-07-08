

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple

from shellparser.components.inputs.InputComponent import InputComponent

import tags


class InputValueType(Enum):
    RUNTIME         = auto()
    ENV_VAR         = auto()
    STRING          = auto()
    NUMERIC         = auto()
    BOOLEAN         = auto()
    NONE            = auto()

enum_map = {
    'runtime': InputValueType.RUNTIME,
    'env_var': InputValueType.ENV_VAR,
    'string': InputValueType.STRING,
    'numeric': InputValueType.NUMERIC,
    'boolean': InputValueType.BOOLEAN,
    'none': InputValueType.NONE
}

@dataclass
class InputValue(ABC):
    component: InputComponent
    linked: bool

    @property
    @abstractmethod
    def abstract_value(self) -> str:
        ...
    
    @property
    def comptype(self) -> Optional[str]:
        return type(self.component).__name__.lower() 
    

@dataclass
class StaticInputValue(InputValue):
    value: str
    _valtypestr: str
    default: bool = False

    def __post_init__(self):
        self.valtype = enum_map[self._valtypestr]
    
    @property
    def abstract_value(self) -> str:
        return self.value


@dataclass
class ConnectionInputValue(InputValue):
    step_uuid: str
    output_uuid: str
    
    @property
    def abstract_value(self) -> str:
        step_tag = tags.workflow.get(self.step_uuid)
        output_tag = tags.workflow.get(self.output_uuid)
        return f'step {step_tag}: {output_tag}'
    

@dataclass
class WorkflowInputInputValue(InputValue):
    input_uuid: str
    is_runtime: bool = False

    @property
    def abstract_value(self) -> str:
        input_tag = tags.workflow.get(self.input_uuid)
        return f'workflow input: {input_tag}'


class InputValueRegister:
    def __init__(self):
        # TODO this will change. Need to account for subworkflows. 
        # inputs_params could be list[InputComponent] when step is toolstep
        # inputs_params could be list[WorkflowInput] in step is subworkflow
        self.input_params: list[InputComponent] 
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
        self.unlinked_values.append(value)
    
    def __str__(self) -> str:
        out: str = '\nInputValueRegister -----\n'
        out += f"{'[gxparam]':30}{'[input type]':30}{'[value]':30}\n"
        for uuid, inp in self.linked_values.items():
            component_tag = tags.tool.get(uuid)
            out += f'{component_tag:30}{str(type(inp).__name__):30}{inp.abstract_value:30}\n'
        return out



