




import json
from typing import Any

from workflows.workflow.Workflow import Workflow
from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.parsing.parsing import parse_step
from datatypes.DatatypeAnnotator import DatatypeAnnotator

class WorkflowFactory:
    """models a galaxy workflow"""
    datatype_annotator: DatatypeAnnotator = DatatypeAnnotator()

    def create(self, workflow_path: str):
        self.tree = self.load_tree(workflow_path)
        self.metadata = self.parse_metadata()
        self.workflow = Workflow(self.metadata)
        self.parse_steps()
        return self.workflow

    def load_tree(self, path: str) -> dict[str, Any]:
        # TODO should probably check the workflow type (.ga, .ga2)
        # and internal format is valid
        with open(path, 'r') as fp:
            return json.load(fp)

    def parse_metadata(self) -> WorkflowMetadata:
        return WorkflowMetadata(
            name=self.tree['name'],
            uuid=self.tree['uuid'],
            annotation=self.tree['annotation'],
            version=self.tree['version'],
            tags=self.tree['tags']
        )

    def parse_steps(self) -> None:
        for step_details in self.tree['steps'].values():
            step = parse_step(step_details)
            self.datatype_annotator.annotate(step)
            self.workflow.add_step(step)

