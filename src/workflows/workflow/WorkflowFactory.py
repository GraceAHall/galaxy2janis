




import json
from typing import Any

from workflows.workflow.Workflow import Workflow
from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.parsing import parse_step
from workflows.step.Step import GalaxyWorkflowStep, InputDataStep, ToolStep
from workflows.io.Output import WorkflowOutput
from command.components.TagFormatter import TagFormatter
#from datatypes.formatting import format_janis_str



class WorkflowFactory:
    """models a galaxy workflow"""
    tag_formatter: TagFormatter = TagFormatter()

    def create(self, workflow_path: str):
        self.tree = self.load_tree(workflow_path)
        self.metadata = self.parse_metadata()
        self.steps = self.parse_steps()
        return Workflow(
            metadata=self.metadata, 
            steps=self.get_tool_steps(),
            inputs=self.get_input_steps(),
            outputs=self.get_outputs()
        )

    def load_tree(self, path: str) -> dict[str, Any]:
        # TODO should probably check the workflow type (.ga, .ga2)
        # and internal format is valid
        with open(path, 'r') as fp:
            return json.load(fp)

    def parse_metadata(self) -> WorkflowMetadata:
        return WorkflowMetadata(
            name=self.tree['name'],
            annotation=self.tree['annotation'],
            format_version=self.tree['format-version'],
            tags=self.tree['tags'],
            uuid=self.tree['uuid'],
            version=self.tree['version']
        )

    def parse_steps(self) -> list[GalaxyWorkflowStep]:
        out: list[GalaxyWorkflowStep] = []
        for step_details in self.tree['steps'].values():
            out.append(parse_step(step_details))
        return out

    def get_tool_steps(self) -> dict[str, ToolStep]:
        out: dict[str, ToolStep] = {}
        for step in self.steps:
            if isinstance(step, ToolStep):
                tag = self.tag_formatter.format(step.get_name())
                assert(tag not in out)
                out[tag] = step
        return out

    def get_input_steps(self) -> dict[str, InputDataStep]:
        out: dict[str, InputDataStep] = {}
        for step in self.steps:
            if isinstance(step, InputDataStep):
                tag = self.tag_formatter.format(step.get_name())
                assert(tag not in out)
                out[tag] = step
        return out

    def get_outputs(self) -> dict[str, WorkflowOutput]:
        out: dict[str, WorkflowOutput] = {}
        tool_steps = self.get_tool_steps()

        for step_tag, step in tool_steps.items():
            for workflow_out in step.metadata.workflow_outputs:
                step_output = step.get_output(workflow_out['output_name'])
                name = f'{step.get_tool_name()}_{workflow_out["output_name"]}'
                output_tag = self.tag_formatter.format(name)
                output = WorkflowOutput( 
                    datatype=step_output.type,
                    source=f"w.{step_tag}.{step_output.name}",
                )
                out[output_tag] = output
        return out

    def init_workflow_output(self, step_tag: str, step: ToolStep, wout_details: dict[str, Any]) -> WorkflowOutput:
        raise NotImplementedError


