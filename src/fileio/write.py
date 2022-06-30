

from entities.workflow.step.step import WorkflowStep
import settings

from entities.tool import Tool
from entities.workflow import Workflow

from formats.tool_definition.JanisToolFormatter import JanisToolFormatter
from formats.workflow_definition.WorkflowTextDefinition import BulkWorkflowTextDefinition, StepwiseWorkflowTextDefinition, WorkflowTextDefinition
from formats.workflow_inputs.inputs import format_input_dict

from paths import DEFAULT_TOOL_OUTDIR




def write_tool(tool: Tool) -> None:
    formatter = JanisToolFormatter(tool)
    tool_definition = formatter.to_janis_definition()
    path = format_tool_def_path(tool)
    with open(path, 'w') as fp:
        fp.write(tool_definition)

def write_step(step: WorkflowStep) -> None:
    raise NotImplementedError()

def write_workflow(workflow: Workflow) -> None:
    raise NotImplementedError()


def format_tool_def_path(tool: Tool) -> str:
    basename = settings.tool.xml_basename()
    if settings.tool.forced_outdir:
        folder = settings.tool.forced_outdir
    else:
        parent = DEFAULT_TOOL_OUTDIR
        folder = f'{parent}/{basename}'
    return f'{folder}/{basename}.py'


# def write_workflow_tools(workflow: Workflow) -> None:
#     for step in workflow.list_steps():
#         formatter = JanisToolFormatter(step.tool)
#         tool_definition = formatter.to_janis_definition()
#         path = f'{esettings.outdir}/{step.metadata.tool_definition_path}'
#         with open(path, 'w') as fp:
#             fp.write(tool_definition)

# def write_workflow(workflow: Workflow) -> None: 
#     write_workflow_tools(esettings, workflow)
#     write_workflow_definitions(esettings, workflow)


# def write_workflow_definitions(workflow: Workflow) -> None:
#     # inputs dict
#     write_inputs_dict(workflow)

#     # main workflow page
#     text_def = BulkWorkflowTextDefinition(workflow)
#     #text_def = StepwiseWorkflowTextDefinition(esettings, workflow)
#     write_main_page(text_def)
    
#     # individual step pages if necessary
#     if isinstance(text_def, StepwiseWorkflowTextDefinition):
#         write_step_pages(text_def)

# def write_inputs_dict(workflow: Workflow) -> None:
#     FMT = 'yaml'
#     path = esettings.outpaths.inputs(format=FMT)
#     text = format_input_dict(workflow, format=FMT)
#     with open(path, 'w') as fp:
#         fp.write(text)

# def write_main_page(text_def: WorkflowTextDefinition) -> None:
#     path = esettings.outpaths.workflow()
#     with open(path, 'w') as fp:
#         fp.write(text_def.format())
        
# def write_step_pages(text_def: StepwiseWorkflowTextDefinition) -> None:
#     for page in text_def.step_pages:
#         with open(page.path, 'w') as fp:
#             fp.write(page.text)

