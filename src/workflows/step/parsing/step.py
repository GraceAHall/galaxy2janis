

from typing import Any
import json
from runtime.settings.ExeSettings import WorkflowExeSettings

from workflows.io.WorkflowInput import WorkflowInput
from workflows.step.WorkflowStep import WorkflowStep
from workflows.workflow.Workflow import Workflow

from .inputs.inputs import InputDataStepParser

from .metadata import parse_step_metadata
from .inputs import parse_step_inputs
from .outputs import parse_step_outputs

from parse_tool import parse_tool
from runtime.settings.settings import create_tool_settings_for_step


### parsing galaxy to steps -----------
def parse_input_step(step: dict[str, Any]) -> WorkflowInput:
    step['tool_state'] = json.loads(step['tool_state'])
    return InputDataStepParser().parse(step)

def parse_tool_step(wsettings: WorkflowExeSettings, step: dict[str, Any], workflow: Workflow) -> WorkflowStep:
    step['tool_state'] = json.loads(step['tool_state'])
    metadata = parse_step_metadata(step)
    tsettings = create_tool_settings_for_step(wsettings, metadata)
    tool = parse_tool(tsettings)

    wstep = WorkflowStep(
        metadata=metadata,
        inputs=parse_step_inputs(step, workflow, tsettings),
        outputs=parse_step_outputs(step),
        tool=tool
    )
    return wstep



    


