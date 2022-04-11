


from dataclasses import dataclass, field
from typing import Any, Optional, Tuple
from command.components.CommandComponent import CommandComponent
from datatypes.JanisDatatype import JanisDatatype

@dataclass
class StepOutput:
    gxvarname: str
    gx_datatypes: list[str]
    is_wflow_out: bool
    wflow_out_label: Optional[str]
    janis_datatypes: list[JanisDatatype] = field(default_factory=list)
    tool_output: Optional[CommandComponent] = None


def init_input_step_output(step: dict[str, Any]) -> StepOutput:
    is_wflow_out, wflow_out_label = get_wflow_out_details(step, 'output')
    return StepOutput(
        gxvarname='output',
        gx_datatypes=step['tool_state']['format'] if 'format' in step['tool_state'] else ['file'],
        is_wflow_out=is_wflow_out,
        wflow_out_label=wflow_out_label
    )

def init_tool_step_output(step: dict[str, Any], output: dict[str, Any]) -> StepOutput:
    is_wflow_out, wflow_out_label = get_wflow_out_details(step, output['name'])
    return StepOutput(
        gxvarname=output['name'],
        gx_datatypes=[output['type']],
        is_wflow_out=is_wflow_out,
        wflow_out_label=wflow_out_label
    )

def get_wflow_out_details(step: dict[str, Any], output_name: str) -> Tuple[bool, Optional[str]]:
    for wflow_out in step['workflow_outputs']:
        if output_name == wflow_out['output_name']:
            return True, wflow_out['label']
    return False, None
