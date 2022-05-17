

import logging

# classes
from startup.ExeSettings import WorkflowExeSettings
from workflows.workflow.WorkflowParser import WorkflowParser
from workflows.workflow.Workflow import Workflow

# modules
from workflows.step.values.linking.link import link_tool_input_values
from workflows.step.outputs.OutputLinker import link_step_outputs_tool_outputs
from workflows.step.parsing.settings import set_tool_paths
from workflows.io.io import set_outputs


"""
file ingests a galaxy workflow, then downloads and translates each tool
to a janis definition
"""

def parse_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    logger = logging.getLogger('gxtool2janis')
    logger.info(f'parsing workflow from {wsettings.workflow}')
    workflow = init_workflow(wsettings)
    link_tool_input_values(wsettings, workflow)
    link_step_outputs_tool_outputs(workflow)
    set_outputs(workflow)
    set_tool_paths(wsettings, workflow)
    return workflow

def init_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    # basic parsing workflow into internal representaiton
    galaxy_workflow_path = wsettings.get_galaxy_workflow_path()
    factory = WorkflowParser(wsettings)
    workflow = factory.create(galaxy_workflow_path)
    return workflow











