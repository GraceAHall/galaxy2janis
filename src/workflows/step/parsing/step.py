

from typing import Any
import json

from workflows.io.WorkflowInput import WorkflowInput
from workflows.step.WorkflowStep import WorkflowStep
from workflows.workflow.Workflow import Workflow
from .InputDataStepParser import InputDataStepParser
from .ToolStepParser import ToolStepParser



### parsing galaxy to steps -----------
def parse_input_step(step: dict[str, Any]) -> WorkflowInput:
    step['tool_state'] = json.loads(step['tool_state'])
    return InputDataStepParser().parse(step)

def parse_tool_step(step: dict[str, Any], workflow: Workflow) -> WorkflowStep:
    step['tool_state'] = json.loads(step['tool_state'])
    return ToolStepParser(workflow).parse(step)


    


