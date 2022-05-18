

from runtime.ExeSettings import ToolExeSettings, WorkflowExeSettings
from tool.Tool import Tool
from workflows.workflow.Workflow import Workflow

from janis.definitions.tool.JanisToolFormatter import JanisToolFormatter
from janis.definitions.workflow.WorkflowTextDefinition import BulkWorkflowTextDefinition, StepwiseWorkflowTextDefinition, WorkflowTextDefinition
#from janis.definitions.workflow.WorkflowTextDefinition import BulkWorkflowTextDefinition

WFLOW_TEXT_DEFINITION_CLS = BulkWorkflowTextDefinition
#WFLOW_TEXT_DEFINITION_CLS = StepwiseWorkflowTextDefinition

def write_tool(esettings: ToolExeSettings, tool: Tool) -> None:
    formatter = JanisToolFormatter(tool)
    tool_definition = formatter.to_janis_definition()
    tool_path = esettings.get_janis_definition_path()
    with open(tool_path, 'w') as fp:
        fp.write(tool_definition)

def write_workflow_tools(workflow: Workflow) -> None:
    for step in workflow.list_steps():
        formatter = JanisToolFormatter(step.tool)
        tool_definition = formatter.to_janis_definition()
        path = step.get_tool_definition_path()
        with open(path, 'w') as fp:
            fp.write(tool_definition)

def write_workflow(esettings: WorkflowExeSettings, workflow: Workflow) -> None:
    # tool definitions
    write_workflow_tools(workflow)

    # workflow definitions
    text_def = WFLOW_TEXT_DEFINITION_CLS(esettings, workflow)
    wflow_path = esettings.get_janis_workflow_path()
    write_main_page(wflow_path, text_def)
    if isinstance(text_def, StepwiseWorkflowTextDefinition):
        write_step_pages(text_def)
    
def write_main_page(path: str, text_def: WorkflowTextDefinition) -> None:
    with open(path, 'w') as fp:
        fp.write(text_def.format())
        
def write_step_pages(text_def: StepwiseWorkflowTextDefinition) -> None:
    for page in text_def.step_pages:
        with open(page.path, 'w') as fp:
            fp.write(page.text)

