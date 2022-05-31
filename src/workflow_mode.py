

import runtime.logging.logging as logging

# classes
from runtime.settings.ExeSettings import WorkflowExeSettings
from workflows.entities.workflow.workflow import Workflow

# modules
from workflows.parsing.workflow.workflow import parse_workflow
from workflows.parsing.workflow.outputs import set_outputs
from workflows.analysis.step_outputs.link import link_step_outputs_tool_outputs
from workflows.analysis.tool_values.linking.link import link_tool_input_values
from file_io.write import write_workflow

"""
file ingests a galaxy workflow, then downloads and translates each tool
to a janis definition
"""

def workflow_mode(wsettings: WorkflowExeSettings) -> Workflow:
    logging.configure_workflow_logging(wsettings)
    logging.msg_parsing_workflow(wsettings.workflow)
    workflow = parse_workflow(wsettings)
    link_tool_input_values(wsettings, workflow)
    link_step_outputs_tool_outputs(workflow)
    set_outputs(workflow)
    set_tool_paths(wsettings, workflow)
    write_workflow(wsettings, workflow)
    return workflow


# after parsing
def set_tool_paths(wsettings: WorkflowExeSettings, workflow: Workflow) -> None:
    # set the text definition filepath for each tool
    tooldir = wsettings.get_janis_tools_dir()
    for step in workflow.list_steps():
        path = f'{tooldir}/{step.tool.metadata.id}/{step.tool.metadata.id}.py'
        step.set_tool_definition_path(path)






