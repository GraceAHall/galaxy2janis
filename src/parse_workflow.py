

# classes
from startup.ExeSettings import WorkflowExeSettings
from workflows.workflow.Workflow import Workflow
from workflows.workflow.WorkflowFactory import WorkflowFactory

# modules
from workflows.step.values.ValueLinker import link_step_values
from workflows.step.tools.assign import assign_tools, assign_tool_paths


"""
file ingests a galaxy workflow, then downloads and translates each tool
to a janis definition
"""

def parse_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    workflow = init_workflow(wsettings)
    assign_tools(wsettings, workflow)
    assign_tool_paths(wsettings, workflow)
    link_step_values(workflow)
    return workflow

def init_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    # basic parsing workflow into internal representaiton
    galaxy_workflow_path = wsettings.get_galaxy_workflow_path()
    factory = WorkflowFactory()
    workflow = factory.create(galaxy_workflow_path)
    return workflow














