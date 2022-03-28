


from typing import Optional 

from startup.settings import load_tool_settings
from startup.ExeSettings import ToolExeSettings
from startup.ExeSettings import WorkflowExeSettings
from parse_tool import parse_tool
from workflows.step.Step import ToolStep
from workflows.workflow.Workflow import Workflow
from workflows.workflow.WorkflowFactory import WorkflowFactory
from workflows.values.ValueLinker import ValueLinker

"""
file ingests a galaxy workflow, then downloads and translates each tool
to a janis definition
"""

def parse_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    workflow = init_workflow(wsettings)
    parse_tools(wsettings, workflow)
    assign_tool_paths(wsettings, workflow)
    link_tool_input_values(workflow)
    update_tool_components(workflow)
    return workflow

def init_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    # basic parsing workflow into internal representaiton
    galaxy_workflow_path = wsettings.get_galaxy_workflow_path()
    factory = WorkflowFactory()
    workflow = factory.create(galaxy_workflow_path)
    return workflow

def parse_tools(wsettings: WorkflowExeSettings, workflow: Workflow) -> None:
    # generate a tool definition for each tool step
    for tag, step in workflow.steps.items():
        args = make_parse_tool_args(tag, step, wsettings)
        tsettings: ToolExeSettings = load_tool_settings(args)
        step.tool = parse_tool(tsettings)

def make_parse_tool_args(tag: str, step: ToolStep, esettings: WorkflowExeSettings) -> dict[str, Optional[str]]:
    return {
        'dir': None,
        'xml': None,
        'remote_url': step.get_uri(),
        'download_dir': esettings.get_xml_wrappers_dir(),
        'outdir': f'{esettings.get_janis_tools_dir()}/{tag}',
        'cachedir': esettings.user_container_cachedir
    }

def assign_tool_paths(wsettings: WorkflowExeSettings, workflow: Workflow) -> None:
    # write a definition for the workflow
    tools_dir = wsettings.get_janis_tools_dir()
    workflow.assign_tool_definition_paths(tools_dir)

def link_tool_input_values(workflow: Workflow) -> None:
    # link workflow tool input values
    linker = ValueLinker(workflow)
    linker.link()

def update_tool_components(workflow: Workflow) -> None:
    # TODO update knowledge of tool components based on linked values - optionality, datatypes
    pass












