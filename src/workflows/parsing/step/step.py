


from typing import Any

from .inputs import parse_step_inputs
from .outputs import parse_step_outputs
from .metadata import parse_step_metadata

from workflows.entities.workflow.workflow import Workflow
from workflows.entities.step.step import WorkflowStep
from runtime.settings.ExeSettings import WorkflowExeSettings
from runtime.settings.settings import create_tool_settings_for_step
from tool_mode import tool_mode


# MODULE ENTRY
def parse_tool_step(wsettings: WorkflowExeSettings, step: dict[str, Any], workflow: Workflow) -> WorkflowStep:
    metadata = parse_step_metadata(step)
    tsettings = create_tool_settings_for_step(wsettings, metadata)
    tool = tool_mode(tsettings)

    wstep = WorkflowStep(
        metadata=metadata,
        inputs=parse_step_inputs(step, workflow, tsettings),
        outputs=parse_step_outputs(step),
        tool=tool
    )
    return wstep




    


