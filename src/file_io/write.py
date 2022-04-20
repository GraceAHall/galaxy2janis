

from startup.ExeSettings import ToolExeSettings, WorkflowExeSettings
from tool.Tool import Tool
from workflows.workflow.Workflow import Workflow

from janis.definitions.tool.JanisToolFormatter import JanisToolFormatter
from janis.definitions.workflow.StepwiseWorkflowDefinitionWriter import StepwiseWorkflowDefinitionWriter
from janis.definitions.workflow.BulkWorkflowDefinitionWriter import BulkWorkflowDefinitionWriter


def write_file(path: str, contents: str) -> None:
    with open(path, 'w') as fp:
        fp.write(contents)

def write_tool(esettings: ToolExeSettings, tool: Tool) -> None:
    formatter = JanisToolFormatter(tool)
    tool_definition = formatter.to_janis_definition()
    tool_path = esettings.get_janis_definition_path()
    write_file(tool_path, tool_definition)

def write_workflow(esettings: WorkflowExeSettings, workflow: Workflow) -> None:
    # tool definitions
    write_workflow_tools(workflow)

    # workflow definition
    writer = StepwiseWorkflowDefinitionWriter(esettings, workflow)
    writer.write()

def write_workflow_tools(workflow: Workflow) -> None:
    for step in workflow.list_steps():
        assert(step.tool)
        formatter = JanisToolFormatter(step.tool)
        tool_definition = formatter.to_janis_definition()
        tool_path = step.get_definition_path()
        write_file(tool_path, tool_definition)

