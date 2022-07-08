


from typing import Any
from entities.workflow.input import WorkflowInput

from entities.workflow import (
    ConnectionInputValue, 
    WorkflowInputInputValue,
    StaticInputValue
)
from entities.workflow.step.outputs import StepOutput
from shellparser.components.inputs.InputComponent import InputComponent

from .. import utils


def static(component: InputComponent, value: Any, default: bool=False) -> StaticInputValue:
    return StaticInputValue(
        component=component,
        linked=False,
        value=value,
        _valtypestr=utils.select_input_value_type(component, value),
        default=default
    )

def connection(component: InputComponent, step_output: StepOutput) -> ConnectionInputValue:
    # something about finding the step & step output
    # 
    return ConnectionInputValue(
        component=component,
        linked=False,
        step_uuid=None,
        output_uuid=None
    )

def workflow_input(component: InputComponent, winp: WorkflowInput, is_runtime: bool=False) -> WorkflowInputInputValue:
    return WorkflowInputInputValue(
        component=component,
        linked=False,
        input_uuid=winp.uuid,
        is_runtime=is_runtime
    )

