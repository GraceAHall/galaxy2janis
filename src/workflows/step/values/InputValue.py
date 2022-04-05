

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from xmltool.param.Param import Param



class InputValueType(Enum):
    WORKFLOW_INPUT  = auto()
    CONNECTION      = auto()
    RUNTIME         = auto()
    ENV_VAR         = auto()
    STRING          = auto()
    NUMERIC         = auto()
    BOOLEAN         = auto()
    NONE            = auto()


@dataclass
class InputValue:
    value: str
    valtype: InputValueType
    comptype: str # this should really be an enum
    gxparam: Optional[Param] = None
    is_default_value: bool = False


