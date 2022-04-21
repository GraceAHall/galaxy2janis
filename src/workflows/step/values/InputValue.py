

from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

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