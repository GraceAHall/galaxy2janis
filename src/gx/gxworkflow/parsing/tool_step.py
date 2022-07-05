

from typing import Any

from entities.workflow import Workflow
from entities.workflow import WorkflowStep

from .step.metadata import parse_step_metadata
from .step.inputs import parse_step_inputs
from .step.outputs import parse_step_outputs
from .tool import parse_step_tool


def ingest_tool_steps(workflow: Workflow, gxworkflow: dict[str, Any]) -> None:
    for step in gxworkflow['steps'].values():
        if step['type'] == 'tool':
            workflow_step = parse_tool_step(workflow, step)
            workflow.add_step(workflow_step)

def parse_tool_step(workflow: Workflow, step: dict[str, Any]) -> WorkflowStep:
    metadata = parse_step_metadata(step)
    tool = parse_step_tool(metadata)
    return WorkflowStep(
        metadata=metadata,
        tool=tool,
        inputs=parse_step_inputs(step, tool, workflow),
        outputs=parse_step_outputs(step)
    )