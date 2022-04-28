

# classes
from startup.ExeSettings import WorkflowExeSettings
from workflows.workflow.WorkflowFactory import WorkflowFactory
from workflows.workflow.Workflow import Workflow

# modules
from workflows.step.values.linking.InputDictValueLinker import link_step_input_values
from workflows.step.outputs.OutputLinker import link_step_outputs_tool_outputs
from workflows.step.tools.assign import set_tools
from workflows.step.tools.assign import set_tool_paths
from workflows.io.io import set_outputs


"""
file ingests a galaxy workflow, then downloads and translates each tool
to a janis definition
"""

def parse_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    workflow = init_workflow(wsettings)
    set_tools(wsettings, workflow)
    link_step_input_values(workflow)
    link_step_outputs_tool_outputs(workflow)
    set_outputs(workflow)
    set_tool_paths(wsettings, workflow)
    return workflow

def init_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    # basic parsing workflow into internal representaiton
    galaxy_workflow_path = wsettings.get_galaxy_workflow_path()
    factory = WorkflowFactory()
    workflow = factory.create(galaxy_workflow_path)
    return workflow











