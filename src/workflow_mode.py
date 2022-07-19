

import logs.logging as logging
import settings
import json

from typing import Any, Optional
from setup import workflow_setup

from entities.workflow import Workflow

from gx.gxworkflow.parsing.metadata import ingest_metadata
from gx.gxworkflow.parsing.inputs import ingest_workflow_inputs
from gx.gxworkflow.parsing.step import ingest_workflow_steps
from gx.gxworkflow.parsing.tool_step.tool import ingest_workflow_tools
from gx.gxworkflow.parsing.tool_step.prepost import ingest_workflow_steps_prepost
from gx.gxworkflow.parsing.tool_step.outputs import ingest_workflow_steps_outputs

from gx.gxworkflow.values import handle_tool_connection_inputs
from gx.gxworkflow.values import handle_tool_runtime_inputs
from gx.gxworkflow.values import handle_tool_static_inputs
from gx.gxworkflow.values import handle_tool_default_inputs

from gx.gxworkflow.updates import update_component_knowledge
from gx.gxworkflow.connections import handle_scattering

from fileio import write_workflow



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

    galaxy = load_tree()
    janis = Workflow()

    # ingesting workflow entities to internal
    ingest_metadata(janis, galaxy)
    ingest_workflow_inputs(janis, galaxy)
    ingest_workflow_steps(janis, galaxy)
    ingest_workflow_tools(janis, galaxy)
    ingest_workflow_steps_prepost(janis, galaxy)
    ingest_workflow_steps_outputs(janis, galaxy) 

    # assigning tool input values
    handle_tool_connection_inputs(janis, galaxy)
    handle_tool_runtime_inputs(janis, galaxy)
    handle_tool_static_inputs(janis, galaxy)
    handle_tool_default_inputs(janis, galaxy)

    update_component_knowledge(janis)
    handle_scattering(janis)
    write_workflow(janis)

def load_tree() -> dict[str, Any]:
    # TODO should probably check the workflow type (.ga, .ga2)
    # and internal format is valid
    with open(settings.workflow.workflow_path, 'r') as fp:
        return json.load(fp)



