




import json
from typing import Any
from runtime.settings.ExeSettings import WorkflowExeSettings

from workflows.entities.workflow.workflow import Workflow
from workflows.entities.workflow.metadata import WorkflowMetadata
from workflows.parsing.step.step import parse_tool_step
from workflows.parsing.workflow.inputs import parse_input_step
from datatypes.DatatypeAnnotator import DatatypeAnnotator


def parse_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    parser = WorkflowParser(wsettings)
    return parser.parse()


class WorkflowParser:
    """models a galaxy workflow"""
    def __init__(self, wsettings: WorkflowExeSettings):
        self.wsettings = wsettings
        self.datatype_annotator: DatatypeAnnotator = DatatypeAnnotator()

    def parse(self) -> Workflow:
        self.tree = self.load_tree(self.wsettings.workflow)
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
                self.datatype_annotator.annotate(workflow_input)  # type: ignore
                self.workflow.add_input(workflow_input)

    def set_tool_steps(self) -> None:
        for step in self.tree['steps'].values():
            if step['type'] == 'tool':
                workflow_step = parse_tool_step(self.wsettings, step, self.workflow)
                self.datatype_annotator.annotate(workflow_step)  # type: ignore
                self.workflow.add_step(workflow_step)


