
from typing import Optional
from command.components.CommandComponent import CommandComponent
from tool.Tool import Tool

from workflows.entities.step.outputs import StepOutput
from workflows.entities.workflow.workflow import Workflow
from workflows.entities.step.step import WorkflowStep



"""
Links step outputs to underlying tool outputs. 
Assigns eaech StepOutput the underlying ToolOutput
"""

# module entry
def link_step_outputs_tool_outputs(workflow: Workflow):
    for step in workflow.list_steps():
        linker = StepToolOutputLinker(step, workflow)
        linker.link()


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


