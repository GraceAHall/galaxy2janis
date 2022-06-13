


import json
from typing import Any
from datatypes.DatatypeAnnotator import DatatypeAnnotator

# classes
from runtime.settings.ExeSettings import WorkflowExeSettings
from workflows.entities.workflow.metadata import WorkflowMetadata
from workflows.entities.workflow.workflow import Workflow
from workflows.parsing.workflow.inputs import parse_input_step
from workflows.parsing.step.step import parse_tool_step
from workflows.parsing.step.inputs import parse_step_inputs
from workflows.parsing.step.outputs import parse_step_outputs


def parse_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    """
    parses Galaxy .ga file into a Workflow.
    the workflow is not fully settled at this point and more
    analysis etc comes later.
    the order here seems weird but trust me there is reason. 
    this is the only time the .ga file is interacted with.
    
    """
    parser = WorkflowParser(wsettings)
    return parser.parse()



class WorkflowParser:
    
    def __init__(self, wsettings: WorkflowExeSettings):
        self.wsettings = wsettings
        self.datatype_annotator: DatatypeAnnotator = DatatypeAnnotator()
        self.tree = self.load_tree(self.wsettings.workflow_path)
    
    def load_tree(self, path: str) -> dict[str, Any]:
        # TODO should probably check the workflow type (.ga, .ga2)
        # and internal format is valid
        with open(path, 'r') as fp:
            return json.load(fp)

    def parse(self) -> Workflow:
        self.init_workflow()
        self.init_inputs()
        self.init_steps()
        # by this point, step_tags & tool_ids are known
        # we can now access all files for logging, downloading,
        # writing definitions etc
        self.init_step_inputs()
        self.init_step_outputs()
        return self.workflow

    def init_workflow(self) -> None:
        self.metadata = self.parse_metadata()
        self.workflow = Workflow(self.metadata)

    def parse_metadata(self) -> WorkflowMetadata:
        return WorkflowMetadata(
            name=self.tree['name'],
            uuid=self.tree['uuid'],
            annotation=self.tree['annotation'],
            version=self.tree['version'],
            tags=self.tree['tags']
        )

    def init_inputs(self) -> None:
        for step in self.tree['steps'].values():
            if step['type'] in ['data_input', 'data_collection_input']:
                workflow_input = parse_input_step(step)
                self.datatype_annotator.annotate(workflow_input)  # type: ignore
                self.workflow.add_input(workflow_input)
    
    def init_steps(self) -> None:
        for step in self.tree['steps'].values():
            if step['type'] == 'tool':
                workflow_step = parse_tool_step(step)
                self.workflow.add_step(workflow_step)
    
    def init_step_inputs(self) -> None:
        for step_id, step in self.tree['steps'].items():
            if step['type'] == 'tool':
                workflow_step = self.workflow.get_step_by_step_id(step_id)
                # TODO HERE
                inputs = parse_step_inputs()
                for inp in inputs:
                    self.datatype_annotator.annotate(workflow_step)  # type: ignore
                    workflow_step.inputs.add(inp)
    
    def init_step_outputs(self) -> None:
        for step_id, step in self.tree['steps'].items():
            if step['type'] == 'tool':
                workflow_step = self.workflow.get_step_by_step_id(step_id)
                # TODO HERE
                outputs = parse_step_outputs()
                for output in outputs:
                    self.datatype_annotator.annotate(workflow_step)  # type: ignore
                    workflow_step.outputs.add(output)



