
from typing import Optional
from shellparser.components.CommandComponent import CommandComponent
from entities.tool import Tool

from entities.workflow import StepOutput
from entities.workflow import Workflow
from entities.workflow import WorkflowStep



"""
Links step outputs to underlying tool outputs. 
Assigns eaech StepOutput the underlying ToolOutput
"""

# module entry
def link_workflow_tool_outputs(workflow: Workflow) -> Workflow:
    for step in workflow.steps():
        linker = StepToolOutputLinker(step, workflow)
        linker.link()
    return workflow


class StepToolOutputLinker:
    def __init__(self, step: WorkflowStep, workflow: Workflow):
        self.step = step
        self.tool: Tool = step.tool # type: ignore
        self.workflow = workflow

    def link(self) -> None:
        for output in self.step.outputs.list():
            output.tool_output = self._get_associated_tool_output(output)

    def _get_associated_tool_output(self, stepout: StepOutput) -> Optional[CommandComponent]:
        # each tool output should have a linked gxparam
        for toolout in self.tool.list_outputs():
            assert(toolout.gxparam)
            if stepout.gx_varname == toolout.gxparam.name:
                return toolout
        raise RuntimeError(f"couldn't find tool output for step output {stepout.gx_varname}")


