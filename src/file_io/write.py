

from startup.ExeSettings import ToolExeSettings, WorkflowExeSettings
from tool.Tool import Tool
from workflows.workflow.Workflow import Workflow

from janis.definitions.tool.JanisToolFormatter import JanisToolFormatter
from janis.definitions.workflow.StepwiseWorkflowTextDefinition import StepwiseWorkflowTextDefinition
from janis.definitions.workflow.BulkWorkflowTextDefinition import BulkWorkflowTextDefinition


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
    writer = BulkWorkflowTextDefinition(esettings, workflow)
    writer.write()
    
def write_to_workflow_page(self, contents: str) -> None:
    filepath = self.get_workflow_page_path()
    with open(filepath, 'w') as fp:
        fp.write(contents)

def get_workflow_page_path(self) -> str:
    return self.esettings.get_janis_workflow_path()


def write_to_step_page(self, step: WorkflowStep, contents: str) -> None:
    filepath = self.get_step_page_path(step)
    with open(filepath, 'w') as fp:
        fp.write(contents)

def get_step_page_path(self, step: WorkflowStep) -> str:
    steps_dir = self.esettings.get_janis_steps_dir()
    step_tag = self.workflow.tag_manager.get(step.get_uuid())
    return os.path.join(steps_dir, step_tag)


def write_workflow_tools(workflow: Workflow) -> None:
    for step in workflow.list_steps():
        assert(step.tool)
        formatter = JanisToolFormatter(step.tool)
        tool_definition = formatter.to_janis_definition()
        tool_path = step.get_definition_path()
        write_file(tool_path, tool_definition)

