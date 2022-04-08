




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

    def parse_inputs(self) -> None:
        # each InputDataStep only has a single step input and output
        for step in workflow.list_input_steps():
            inp = step.list_inputs()[0]
            out = step.list_outputs()[0]
            #entity_info = {'name': inp.name}
            #name = TagFormatter().format(entity_info)
            step_id = step.metadata.step_id
            step_tag = workflow.get_step_tag_by_step_id(step_id)
            new_input = WorkflowInput(
                step_id=step_id,
                step_tag=step_tag,
                step_input=inp.gxvarname,
                janis_datatypes=out.janis_datatypes,
                is_galaxy_input_step=True
            )
            workflow.add_input(new_input)
            #workflow.steps_inputs_uuid_map[step.get_uuid()] = new_input.get_uuid()

    def parse_steps(self) -> None:
        for step_details in self.tree['steps'].values():
            if 
            step = parse_step(step_details)
            self.datatype_annotator.annotate(step)
            self.workflow.add_step(step)

    def set_workflow_outputs(workflow: Workflow) -> None:
        for step in workflow.list_tool_steps():
            assert(step.tool)
            for out in step.list_outputs():
                if out.is_wflow_out:
                    step_tag = workflow.tag_manager.get(step.get_uuid())
                    workflow.add_output(WorkflowOutput(
                        step_id=step.metadata.step_id,
                        step_tag=step_tag,
                        step_output=out.gxvarname,
                        janis_datatypes=out.janis_datatypes
                    ))

