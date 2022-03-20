

from typing import Any

from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.Step import GalaxyWorkflowStep, InputDataStep, ToolStep
from workflows.io.Output import WorkflowOutput


class Workflow:
    def __init__(self, metadata: WorkflowMetadata, steps: list[GalaxyWorkflowStep]) -> None:
        self.metadata = metadata
        self.steps = steps

    def get_inputs(self) -> list[InputDataStep]:
        out: list[InputDataStep] = []
        for step in self.steps:
            if isinstance(step, InputDataStep):
                out.append(step)
        return out

    def get_tool_steps(self) -> list[ToolStep]:
        out: list[ToolStep] = []
        for step in self.steps:
            if isinstance(step, ToolStep):
                out.append(step)
        out.sort(key=lambda x: x.metadata.step_id)
        return out

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

    def to_janis_definition(self) -> str:
        raise NotImplementedError()
    
