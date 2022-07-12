

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

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
    #'runtime': InputValueType.RUNTIME,
    'env_var': InputValueType.ENV_VAR,
    'string': InputValueType.STRING,
    'numeric': InputValueType.NUMERIC,
    'boolean': InputValueType.BOOLEAN,
    'none': InputValueType.NONE
}

@dataclass
class InputValue(ABC):
    component: Optional[InputComponent]

    @property
    @abstractmethod
    def tag_and_value(self) -> str:
        ...
    
    @property
    def comptype(self) -> Optional[str]:
        return type(self.component).__name__.lower() 
    
    @property
    def input_tag(self) -> Optional[str]:
        if self.component:
            return tags.tool.get(self.component.uuid)
        else:
            return '#UNKNOWN'
    

@dataclass
class StaticInputValue(InputValue):
    value: str
    _valtypestr: str
    default: bool

    def __post_init__(self):
        self.valtype = enum_map[self._valtypestr]
    
    @property
    def is_none(self) -> bool:
        if self.valtype == InputValueType.NONE:
            return True
        return False
    
    @property
    def tag_and_value(self) -> str:
        if self._should_wrap_value():
            return f'{self.input_tag}="{self.value}"'
        else:
            return f'{self.input_tag}={self.value}'

    def _should_wrap_value(self) -> bool:
        if self.valtype == InputValueType.STRING:
            return True
        if self.valtype == InputValueType.ENV_VAR:
            return True
        return False


@dataclass
class ConnectionInputValue(InputValue):
    step_uuid: str
    output_uuid: str
    
    @property
    def tag_and_value(self) -> str:
        step_tag = tags.workflow.get(self.step_uuid)
        output_tag = tags.workflow.get(self.output_uuid)
        return f'{self.input_tag}=w.{step_tag}.{output_tag}'
    

@dataclass
class WorkflowInputInputValue(InputValue):
    input_uuid: str
    is_runtime: bool

    @property
    def tag_and_value(self) -> str:
        winp_tag = tags.workflow.get(self.input_uuid)
        return f'{self.input_tag}=w.{winp_tag}'

