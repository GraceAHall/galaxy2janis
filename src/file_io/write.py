

from runtime.settings.ExeSettings import ToolExeSettings, WorkflowExeSettings
from tool.Tool import Tool
from workflows.entities.workflow.workflow import Workflow

from janis.formats.tool_definition.JanisToolFormatter import JanisToolFormatter
from janis.formats.workflow_definition.WorkflowTextDefinition import BulkWorkflowTextDefinition, StepwiseWorkflowTextDefinition, WorkflowTextDefinition
from janis.formats.workflow_inputs.inputs import format_input_dict


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
        path = step.tool_definition_path
        with open(path, 'w') as fp:
            fp.write(tool_definition)

def write_workflow(esettings: WorkflowExeSettings, workflow: Workflow) -> None: 
    write_workflow_tools(workflow)
    write_workflow_definitions(esettings, workflow)


def write_workflow_definitions(esettings: WorkflowExeSettings, workflow: Workflow) -> None:
    # inputs dict
    write_inputs_dict(esettings, workflow)

    # main workflow page
    text_def = BulkWorkflowTextDefinition(esettings, workflow)
    #text_def = StepwiseWorkflowTextDefinition(esettings, workflow)
    write_main_page(esettings, text_def)
    
    # individual step pages if necessary
    if isinstance(text_def, StepwiseWorkflowTextDefinition):
        write_step_pages(text_def)

def write_inputs_dict(esettings: WorkflowExeSettings, workflow: Workflow) -> None:
    FMT = 'yaml'
    path = esettings.get_janis_input_dict_path(format=FMT)
    text = format_input_dict(workflow, format=FMT)
    with open(path, 'w') as fp:
        fp.write(text)

def write_main_page(esettings: WorkflowExeSettings, text_def: WorkflowTextDefinition) -> None:
    path = esettings.get_janis_workflow_path()
    with open(path, 'w') as fp:
        fp.write(text_def.format())
        
def write_step_pages(text_def: StepwiseWorkflowTextDefinition) -> None:
    for page in text_def.step_pages:
        with open(page.path, 'w') as fp:
            fp.write(page.text)

