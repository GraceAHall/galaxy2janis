

from startup.ExeSettings import ToolExeSettings, WorkflowExeSettings
from tool.Tool import Tool
from workflows.workflow.Workflow import Workflow


def write_file(path: str, contents: str) -> None:
    with open(path, 'w') as fp:
        fp.write(contents)

def write_tool(esettings: ToolExeSettings, tool: Tool) -> None:
    tool_path = esettings.get_janis_definition_path()
    tool_definition = tool.to_janis_definition()
    write_file(tool_path, tool_definition)

def write_workflow(esettings: WorkflowExeSettings, workflow: Workflow) -> None:
    write_workflow_tools(esettings, workflow)
    write_workflow_steps(esettings, workflow)
    write_workflow_config(esettings, workflow)
    write_workflow_definition(esettings, workflow)

def write_workflow_steps(esettings: WorkflowExeSettings, workflow: Workflow) -> None:
    pass

def write_workflow_config(esettings: WorkflowExeSettings, workflow: Workflow) -> None:
    pass

def write_workflow_definition(esettings: WorkflowExeSettings, workflow: Workflow) -> None:
    workflow_path = esettings.get_janis_workflow_path()
    workflow_definition = workflow.to_janis_definition()
    write_file(workflow_path, workflow_definition)

def write_workflow_tools(esettings: WorkflowExeSettings, workflow: Workflow) -> None:
    for tag, step in workflow.steps.items():
        tool_path = f'{esettings.get_janis_tools_dir()}/{tag}.py'
        tool_definition = step.tool.to_janis_definition()  # type: ignore
        write_file(tool_path, tool_definition)

