



from abc import ABC
from dataclasses import dataclass
from typing import Any, Optional

from xmltool.param.Param import Param


@dataclass
class StepInput(ABC):
    name: str

    def __post_init__(self):
        self.linked: bool = False
        self.gxparam: Optional[Param] = None

@dataclass
class ConnectionStepInput(StepInput):
    step_id: int
    output_name: str

@dataclass
class StaticStepInput(StepInput):
    value: str

@dataclass
class RuntimeStepInput(StepInput):
    description: str # not really needed
    value: str = 'USER_DEFINED'
    

def init_connection_step_input(name: str, details: dict[str, Any]) -> StepInput:
    name = name.replace('|', '.')
    return ConnectionStepInput(
        name=name,
        step_id=details['id'],
        output_name=details['output_name']
    )

def init_userdefined_step_input(details: dict[str, Any]) -> StepInput:
    return RuntimeStepInput(
        name=details['name'],
        description=details['description']
    )

def init_static_step_input(name: str, value: Any) -> StepInput:
    return StaticStepInput(
        name=name,
        value=value
    )

