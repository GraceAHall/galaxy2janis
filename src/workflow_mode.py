

import logs.logging as logging
import settings
import json
import tags

from typing import Any, Optional
from setup import workflow_setup

from entities.workflow import Workflow
from entities.workflow import WorkflowOutput

from gx.gxworkflow.parsing.metadata import ingest_metadata
from gx.gxworkflow.parsing.input_step import ingest_input_steps
from gx.gxworkflow.parsing.tool_step import ingest_tool_steps

from gx.gxworkflow.analysis.tool_values.linking.link import link_workflow_tool_values

from fileio import write_workflow

# from workflows.parsing.workflow.inputs import parse_input_step
# from workflows.parsing.step.step import parse_tool_step

# from workflows.parsing.step.inputs import parse_step_inputs
# from workflows.parsing.step.outputs import parse_step_outputs

# from workflows.parsing.tools.tools import parse_workflow_tools
# from gx.gxworkflow.analysis.step_outputs.link import link_workflow_tool_outputs
# from workflows.parsing.workflow.outputs import init_workflow_outputs


"""
this file is the overall orchestrator to parse 
a galaxy workflow to janis. 
class approach used just to reduce number of variables
being passed to functions here (clutter) and to reduce
the number of times certain files are loaded (speed)
the order here seems weird but trust me there is reason. 
"""

def workflow_mode(args: dict[str, Optional[str]]) -> None:
    workflow_setup(args)
    logging.msg_parsing_workflow()
    gxworkflow = load_tree()
    workflow = Workflow()

    # parse inputs & steps.
    # parse each tool needed in each step. 
    ingest_metadata(workflow, gxworkflow)
    ingest_input_steps(workflow, gxworkflow)
    ingest_tool_steps(workflow, gxworkflow)
    link_workflow_tool_values(workflow)
    #link_tool_step_outputs(workflow)
    #create_workflow_outputs(workflow)
    
    write_workflow(workflow)


def load_tree() -> dict[str, Any]:
    # TODO should probably check the workflow type (.ga, .ga2)
    # and internal format is valid
    with open(settings.workflow.workflow_path, 'r') as fp:
        return json.load(fp)

def create_workflow_outputs(workflow: Workflow) -> Workflow:
    for step in workflow.steps:
        for stepout in step.outputs.list():
            if stepout.is_wflow_out:
                toolout = stepout.tool_output
                assert(toolout)
                workflow_output = WorkflowOutput(
                    step_tag=tags.workflow.get(step.uuid),
                    toolout_tag=tags.tool.get(toolout.uuid),
                    janis_datatypes=stepout.janis_datatypes
                )
                workflow.add_output(workflow_output)
    return workflow

