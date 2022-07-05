

from typing import Any
from entities.workflow import StepOutput
from entities.workflow import StepOutputRegister


def parse_step_outputs(step: dict[str, Any]) -> StepOutputRegister:
    outputs = [init_tool_step_output(step, out) for out in step['outputs']]
    register = StepOutputRegister()
    for out in outputs:
        register.add(out)
    return register

def init_tool_step_output(step: dict[str, Any], output: dict[str, Any]) -> StepOutput:
    return StepOutput(
        gx_varname=output['name'],
        gx_datatypes=output['type'].split(','),
        is_wflow_out=is_workflow_output(step, output),
    )

def is_workflow_output(step: dict[str, Any], output: dict[str, Any]) -> bool:
    if step['workflow_outputs']:
        for details in step['workflow_outputs']:
            if details['output_name'] == output['name']:
                return True
    elif not step['workflow_outputs']:
        return True
    return False