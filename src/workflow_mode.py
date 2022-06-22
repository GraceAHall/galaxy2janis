
import logs.logging as logging
import json
from typing import Any, Optional

import settings.workflow.settings as wsettings

import datatypes
from entities.workflow.metadata import WorkflowMetadata
from entities.workflow.workflow import Workflow
from workflows.parsing.workflow.inputs import parse_input_step
from workflows.parsing.step.step import parse_tool_step

from workflows.parsing.step.inputs import parse_step_inputs
from workflows.parsing.step.outputs import parse_step_outputs

from workflows.parsing.tools.tools import parse_workflow_tools
from workflows.analysis.tool_values.linking.link import link_workflow_tool_values
from workflows.analysis.step_outputs.link import link_workflow_tool_outputs
from workflows.parsing.workflow.outputs import init_workflow_outputs



"""
this file is the overall orchestrator to parse 
a galaxy workflow to janis. 
class approach used just to reduce number of variables
being passed to functions here (clutter) and to reduce
the number of times certain files are loaded (speed)
the order here seems weird but trust me there is reason. 
"""

def workflow_mode(args: dict[str, Optional[str]]) -> None:
    # setup
    esettings = load_workflow_settings(args)
    logging.configure_workflow_logging(esettings)
    logging.msg_parsing_workflow(esettings.workflow_path)

    # main
    parser = WorkflowParser(esettings)
    workflow = parser.init_workflow()
    workflow = parser.init_workflow_inputs(workflow)
    workflow = parser.init_workflow_steps(workflow)
    
    # by this point, step_tags & tool_ids are known
    # need to take a brief pause to init output folder structure 
    # and download wrappers.
    init_workflow_folders(workflow, esettings)
    fetch_workflow_wrappers(workflow, esettings)
    
    # can now access all files (including wrapper xml) 
    # for loading, logging, writing definitions etc
    workflow = parser.init_workflow_step_inputs(workflow)
    workflow = parser.init_workflow_step_outputs(workflow)

    # galaxy workflow parsed at this point
    # now must parse tools to janis, create
    # values for tool inputs in each step 
    # finalise workflow inputs / outputs etc
    workflow = parse_workflow_tools(workflow)
    workflow = link_workflow_tool_values(workflow, esettings)
    workflow = link_workflow_tool_outputs(workflow)
    workflow = init_workflow_outputs(workflow)

    write_workflow(esettings, workflow)



class WorkflowParser:
    
    def __init__(self):
        self.tree = self.load_tree(wsettings.workflow_path)
    
    def load_tree(self, path: str) -> dict[str, Any]:
        # TODO should probably check the workflow type (.ga, .ga2)
        # and internal format is valid
        with open(path, 'r') as fp:
            return json.load(fp)

    def init_workflow(self) -> Workflow:
        """could also just create empty workflow but that sucks"""
        metadata = self.parse_metadata()
        return Workflow(metadata)

    def parse_metadata(self) -> WorkflowMetadata:
        """scrape basic workflow metadata"""
        return WorkflowMetadata(
            name=self.tree['name'],
            uuid=self.tree['uuid'],
            annotation=self.tree['annotation'],
            version=self.tree['version'],
            tags=self.tree['tags']
        )

    def init_workflow_inputs(self, workflow: Workflow) -> Workflow:
        """registers each galaxy 'input step' as a workflow input"""
        for step in self.tree['steps'].values():
            if step['type'] in ['data_input', 'data_collection_input']:
                workflow_input = parse_input_step(step)
                datatypes.annotate(workflow_input)  # type: ignore
                workflow.add_input(workflow_input)
        return workflow
    
    def init_workflow_steps(self, workflow: Workflow) -> Workflow:
        """
        Basic initialisation for each step. 
        Exists because we must finalise step tags 
        before doing other operations.
        """
        for step in self.tree['steps'].values():
            if step['type'] == 'tool':
                workflow_step = parse_tool_step(step)
                workflow.add_step(workflow_step)
        return workflow
    
    def init_workflow_step_inputs(self, workflow: Workflow) -> Workflow:
        """
        for each step, ingest tool_state into 
        register of inputs. inputs are resolved 
        to underlying values for some params.
        """
        for step_id, step in self.tree['steps'].items():
            if step['type'] == 'tool':
                workflow_step = workflow.get_step_by_step_id(step_id)
                # TODO HERE
                inputs = parse_step_inputs()
                for inp in inputs:
                    datatypes.annotate(workflow_step)  # type: ignore
                    workflow_step.inputs.add(inp)
        return workflow
    
    def init_workflow_step_outputs(self, workflow: Workflow) -> Workflow:
        """for each step, identify outputs"""
        for step_id, step in self.tree['steps'].items():
            if step['type'] == 'tool':
                workflow_step = workflow.get_step_by_step_id(step_id)
                # TODO HERE
                outputs = parse_step_outputs()
                for output in outputs:
                    datatypes.annotate(workflow_step)  # type: ignore
                    workflow_step.outputs.add(output)
        return workflow




