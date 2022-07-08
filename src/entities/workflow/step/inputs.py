


from abc import ABC
from dataclasses import dataclass
from typing import Optional
from gx.gxtool.param.Param import Param
from shellparser.components.inputs.InputComponent import InputComponent


@dataclass
class StepInput(ABC):

    def __post_init__(self):
        self.linked: bool = False


@dataclass
class WorkflowInputStepInput(StepInput):
    input_uuid: str
    target: Optional[InputComponent]

@dataclass
class ConnectionStepInput(StepInput):
    step_uuid: str
    output_uuid: str
    target: Optional[InputComponent]

@dataclass
class RuntimeStepInput(StepInput):
    target: Optional[InputComponent]

@dataclass
class StaticStepInput(StepInput):
    gxparam: Param
    value: str





