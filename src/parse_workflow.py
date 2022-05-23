

import runtime.logging.logging as logging

# classes
from runtime.settings.ExeSettings import WorkflowExeSettings
from workflows.workflow.WorkflowParser import WorkflowParser
from workflows.workflow.Workflow import Workflow

# modules
from workflows.step.values.linking.link import link_tool_input_values
from workflows.step.outputs.OutputLinker import link_step_outputs_tool_outputs
from workflows.io.io import set_outputs




"""
file ingests a galaxy workflow, then downloads and translates each tool
to a janis definition
"""

def parse_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    logging.configure_workflow_logging(wsettings)
    logging.msg_parsing_workflow(wsettings.workflow)
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

# after parsing
def set_tool_paths(wsettings: WorkflowExeSettings, workflow: Workflow) -> None:
    # set the text definition filepath for each tool
    tooldir = wsettings.get_janis_tools_dir()
    for step in workflow.list_steps():
        path = f'{tooldir}/{step.tool.metadata.id}/{step.tool.metadata.id}.py'
        step.set_tool_definition_path(path)






