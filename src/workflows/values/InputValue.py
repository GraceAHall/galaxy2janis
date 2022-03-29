

from dataclasses import dataclass
from enum import Enum, auto



class InputValueType(Enum):
    CONNECTION      = auto()
    RUNTIME_VALUE   = auto()
    STRING          = auto()
    NUMERIC         = auto()
    BOOLEAN         = auto()
    NONE            = auto()


@dataclass
class InputValue:
    valtype: InputValueType
    value: str


