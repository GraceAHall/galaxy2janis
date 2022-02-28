

from typing import Iterable
from .Step import ToolStep
from .Workflow import Workflow


example = {
    "tool_shed_repository": {
        "changeset_revision": "1d8fe9bc4cb0",
        "name": "fastp",
        "owner": "iuc",
        "tool_shed": "toolshed.g2.bx.psu.edu"
    },
}


class WorkflowInteractor:
    workflow: Workflow

    def load_workflow(self, wflowpath: str):
        self.workflow = Workflow(wflowpath)

    def iter_tool_steps(self) -> Iterable[ToolStep]:
        for step in self.workflow.steps.values():
            if isinstance(step, ToolStep):
                yield step
        
