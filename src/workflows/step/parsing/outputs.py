

from typing import Any

from workflows.step.outputs.StepOutputRegister import StepOutputRegister
from workflows.step.outputs.StepOutput import init_tool_step_output


def parse_step_outputs(gxstep: dict[str, Any]) -> StepOutputRegister:
    step_outputs = [init_tool_step_output(gxstep, out) for out in gxstep['outputs']]
    return StepOutputRegister(step_outputs)