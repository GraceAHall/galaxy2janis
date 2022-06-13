

import runtime.logging.logging as logging

# classes
from runtime.settings.ExeSettings import WorkflowExeSettings

# modules
from workflows.parsing.workflow.workflow import parse_workflow
from workflows.parsing.workflow.outputs import set_outputs
from workflows.analysis.tool_values.linking.link import link_tool_values
from workflows.analysis.step_outputs.link import link_tool_outputs
from file_io.write import write_workflow

"""
file ingests a galaxy workflow, then downloads and translates each tool
to a janis definition
"""

def workflow_mode(wsettings: WorkflowExeSettings) -> None:
    logging.configure_workflow_logging(wsettings)
    logging.msg_parsing_workflow(wsettings.workflow_path)

    workflow = parse_workflow(wsettings)
    
    set_tools()
    link_tool_values()
    link_tool_outputs()
    set_outputs()

    write_workflow(wsettings, workflow)


