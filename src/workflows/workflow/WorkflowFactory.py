




import json
from typing import Any

from workflows.workflow.Workflow import Workflow
from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.parsing import parse_step
from workflows.step.Step import GalaxyWorkflowStep


class WorkflowFactory:
    """models a galaxy workflow"""

    def create(self, workflow_path: str):
        self.tree = self.load_tree(workflow_path)
        self.metadata: WorkflowMetadata = self.parse_metadata()
        self.steps: list[GalaxyWorkflowStep] = self.parse_steps()
        return Workflow(self.metadata, self.steps)

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


