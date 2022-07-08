

import logs.logging as logging
import settings
import json

from typing import Any, Optional
from setup import workflow_setup

from entities.workflow import Workflow

from gx.gxworkflow.parsing.metadata import ingest_metadata
from gx.gxworkflow.parsing.inputs import ingest_workflow_inputs
from gx.gxworkflow.parsing.step import ingest_workflow_steps

# WORKING
from gx.gxworkflow.parsing.tool_step.tool import ingest_workflow_steps_tools
from gx.gxworkflow.parsing.tool_step.outputs import ingest_workflow_steps_outputs
from gx.gxworkflow.parsing.tool_step.inputs import ingest_workflow_steps_inputs

from gx.gxworkflow.values.link import link_step_tool_values

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

    ingest_metadata(janis, galaxy)
    ingest_workflow_inputs(janis, galaxy)
    ingest_workflow_steps(janis, galaxy)
    ingest_workflow_steps_tools(janis)
    ingest_workflow_steps_outputs(janis, galaxy)
    ingest_workflow_steps_inputs(janis, galaxy)
    link_step_tool_values(janis)
    write_workflow(janis, path)

def load_tree() -> dict[str, Any]:
    # TODO should probably check the workflow type (.ga, .ga2)
    # and internal format is valid
    with open(settings.workflow.workflow_path, 'r') as fp:
        return json.load(fp)



