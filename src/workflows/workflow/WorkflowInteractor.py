

from typing import Any
from workflows.step.Step import InputDataStep, ToolStep
from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from .Workflow import Workflow
from workflows.io.Output import WorkflowOutput
from workflows.io.Input import WorkflowInput

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
        print()

    def get_metadata(self) -> WorkflowMetadata:
        return self.workflow.metadata

    def get_tool_steps(self) -> list[ToolStep]:
        out: list[ToolStep] = []
        for step in self.workflow.steps:
            if isinstance(step, ToolStep):
                out.append(step)
        out.sort(key=lambda x: x.metadata.step_id)
        return out
       
    def get_inputs(self) -> list[WorkflowInput]:
        out: list[WorkflowInput] = []
        for step in self.workflow.steps:
            if isinstance(step, InputDataStep):
                out.append(self.init_workflow_input(step))
        return out

    def init_workflow_input(self, step: InputDataStep) -> WorkflowInput:
        pass

    def get_outputs(self) -> list[WorkflowOutput]:
        out: list[WorkflowOutput] = []
        for step in self.get_tool_steps():
            for wout in step.metadata.workflow_outputs:
                out.append(self.init_workflow_output(step, wout))
        return out

    def init_workflow_output(self, step: ToolStep, wout_details: dict[str, Any]) -> WorkflowOutput:
        step_output = step.get_output(wout_details['output_name'])
        name = f'{step.metadata.tool_name}_{wout_details["output_name"]}'
        return WorkflowOutput(
            name=name,
            step=step.metadata.step_id,
            output_name=wout_details['label'] if wout_details['label'] else name,
            datatype=step_output.type
        )
