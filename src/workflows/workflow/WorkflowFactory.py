




import json
from typing import Any
from workflows.io.WorkflowOutput import WorkflowOutput

from workflows.workflow.Workflow import Workflow
from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.parsing.parse import parse_input_step, parse_tool_step
from datatypes.DatatypeAnnotator import DatatypeAnnotator

class WorkflowFactory:
    """models a galaxy workflow"""
    datatype_annotator: DatatypeAnnotator = DatatypeAnnotator()

    def create(self, workflow_path: str):
        self.tree = self.load_tree(workflow_path)
        self.metadata = self.get_metadata()
        self.workflow = Workflow(self.metadata)
        self.set_inputs()
        self.set_tool_steps()
        return self.workflow

    def load_tree(self, path: str) -> dict[str, Any]:
        # TODO should probably check the workflow type (.ga, .ga2)
        # and internal format is valid
        with open(path, 'r') as fp:
            return json.load(fp)

    def get_metadata(self) -> WorkflowMetadata:
        return WorkflowMetadata(
            name=self.tree['name'],
            uuid=self.tree['uuid'],
            annotation=self.tree['annotation'],
            version=self.tree['version'],
            tags=self.tree['tags']
        )

    def set_inputs(self) -> None:
        for step in self.tree['steps'].values():
            if step['type'] in ['data_input', 'data_collection_input']:
                workflow_input = parse_input_step(step)
                self.datatype_annotator.annotate(workflow_input)
                self.workflow.add_input(workflow_input)

    def set_tool_steps(self) -> None:
        for step in self.tree['steps'].values():
            if step['type'] == 'tool':
                workflow_step = parse_tool_step(step, self.workflow)
                self.datatype_annotator.annotate(workflow_step)
                self.workflow.add_step(workflow_step)


