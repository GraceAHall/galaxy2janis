



from abc import ABC
from dataclasses import dataclass
from typing import Any, Optional
from xmltool.param.Param import Param


@dataclass
class StepInput(ABC):
    gxvarname: str

    def __post_init__(self):
        self.linked: bool = False
        self.gxparam: Optional[Param] = None


@dataclass
class WorkflowInputStepInput(StepInput):
    step_id: int

@dataclass
class ConnectionStepInput(StepInput):
    step_id: int
    output_name: str

@dataclass
class StaticStepInput(StepInput):
    value: str

@dataclass
class RuntimeStepInput(StepInput):
    value: str = 'RuntimeValue'


def init_workflow_input_step_input(name: str, details: dict[str, Any]) -> StepInput:
    name = name.replace('|', '.')
    return WorkflowInputStepInput(
        gxvarname=name,
        step_id=details['id']
    )

def init_connection_step_input(name: str, details: dict[str, Any]) -> StepInput:
    name = name.replace('|', '.')
    return ConnectionStepInput(
        gxvarname=name,
        step_id=details['id'],
        output_name=details['output_name']
    )

def init_runtime_step_input(name: str) -> StepInput:
    return RuntimeStepInput(
        gxvarname=name
    )

def init_static_step_input(name: str, value: Any) -> StepInput:
    return StaticStepInput(
        gxvarname=name,
        value=value
    )

