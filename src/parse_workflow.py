


from typing import Optional 

from startup.settings import load_tool_settings
from startup.ExeSettings import ToolExeSettings
from startup.ExeSettings import WorkflowExeSettings
from parse_tool import parse_tool
from workflows.step.Step import ToolStep
from workflows.workflow.Workflow import Workflow
from workflows.workflow.WorkflowFactory import WorkflowFactory


"""
file ingests a galaxy workflow, then downloads and translates each tool
to a janis definition
"""

def parse_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    # basic parsing workflow into internal representaiton
    galaxy_workflow_path = wsettings.get_galaxy_workflow_path()
    factory = WorkflowFactory()
    workflow = factory.create(galaxy_workflow_path)

    # generate a tool definition for each tool step
    for tag, step in workflow.steps.items():
        args = make_parse_tool_args(tag, step, wsettings)
        tsettings: ToolExeSettings = load_tool_settings(args)
        step.tool = parse_tool(tsettings)

    # write a definition for the workflow
    workflow.assign_step_values()
    
    # TODO update information about tool Components - optionality, datatypes? 
    return workflow


def make_parse_tool_args(tag: str, step: ToolStep, esettings: WorkflowExeSettings) -> dict[str, Optional[str]]:
    return {
        'dir': None,
        'xml': None,
        'remote_url': step.get_uri(),
        'download_dir': esettings.get_xml_wrappers_dir(),
        'outdir': f'{esettings.get_janis_tools_dir()}/{tag}',
        'cachedir': esettings.container_cachedir
    }









