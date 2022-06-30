


from abc import ABC
from dataclasses import dataclass
from typing import Optional
from gx.xmltool.param.Param import Param


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







