

# classes
from startup.ExeSettings import WorkflowExeSettings
from workflows.workflow.Workflow import Workflow
from workflows.workflow.WorkflowFactory import WorkflowFactory

# modules
from workflows.step.values.ValueLinker import link_step_values
from workflows.step.tools.assign import assign_tools, assign_tool_paths
from workflows.io.io import generate_io

"""
file ingests a galaxy workflow, then downloads and translates each tool
to a janis definition
"""

def parse_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    workflow = init_workflow(wsettings)
    workflow.register_step_tags()
    assign_tools(wsettings, workflow)
    workflow.register_tool_tags()
    assign_tool_paths(wsettings, workflow)
    link_step_values(workflow)
    generate_io(workflow)
    migrate_input_data_step_connections_to_w_inputs(workflow)
    return workflow

def init_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    # basic parsing workflow into internal representaiton
    galaxy_workflow_path = wsettings.get_galaxy_workflow_path()
    factory = WorkflowFactory()
    workflow = factory.create(galaxy_workflow_path)
    return workflow

def migrate_input_data_step_connections_to_w_inputs(workflow: Workflow) -> None:
    pass
    #for step_id, step in workflow.get_tool_steps()













