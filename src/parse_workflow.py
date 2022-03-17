


from typing import Optional 

from startup.settings import load_workflow_settings
from startup.ExeSettings import WorkflowExeSettings


from parse_tool import parse_tool
from workflows.step.Step import ToolStep
from workflows.workflow.WorkflowInteractor import WorkflowInteractor


"""
file ingests a galaxy workflow, then downloads and translates each tool
to a janis definition
"""

def parse_workflow(args: dict[str, Optional[str]]):
    esettings: WorkflowExeSettings = load_workflow_settings(args)
    interactor: WorkflowInteractor = WorkflowInteractor()
    interactor.load_workflow(esettings.get_workflow_path())

    # for step in interactor.get_tool_steps():
    #     args = make_parse_tool_args(step, esettings)
    #     parse_tool(args)
    
    print('done')


def make_parse_tool_args(step: ToolStep, esettings: WorkflowExeSettings) -> dict[str, Optional[str]]:
    return {
        'dir': None,
        'xml': None,
        'remote_url': step.get_uri(),
        'outdir': esettings.get_parent_outdir(),
        'cachedir': esettings.container_cachedir
    }




