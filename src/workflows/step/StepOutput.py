


from dataclasses import dataclass
from typing import Any, Optional, Tuple


@dataclass
class StepOutput:
    name: str
    type: str
    is_wflow_out: bool
    wflow_out_label: Optional[str]


def init_step_output(step: dict[str, Any], output: dict[str, str]) -> StepOutput:
    is_wflow_out, wflow_out_label = get_wflow_out_details(step, output)
    return StepOutput(
        output['name'],
        output['type'],
        is_wflow_out=is_wflow_out,
        wflow_out_label=wflow_out_label
    )

def get_wflow_out_details(step: dict[str, Any], output: dict[str, str]) -> Tuple[bool, Optional[str]]:
    for wflow_out in step['workflow_outputs']:
        if output['name'] == wflow_out['output_name']:
            return True, wflow_out['label']
    return False, None
