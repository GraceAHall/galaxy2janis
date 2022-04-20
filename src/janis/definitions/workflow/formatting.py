


from typing import Optional, Tuple
from workflows.io.WorkflowInput import WorkflowInput
from workflows.io.WorkflowOutput import WorkflowOutput
from workflows.step.WorkflowStep import WorkflowStep
from workflows.step.values.InputValue import ConnectionInputValue, InputValue, InputValueType, StaticInputValue, WorkflowInputInputValue
from workflows.workflow.Workflow import Workflow
import janis.definitions.workflow.snippets as snippets


def format_top_note(workflow: Workflow) -> str:
    metadata = workflow.metadata
    return snippets.gxtool2janis_note_snippet(
        workflow_name=metadata.name,
        workflow_version=metadata.version
    )


def format_path_appends() -> str:
    return snippets.path_append_snippet()


def format_metadata(workflow: Workflow) -> str:
    metadata = workflow.metadata
    return snippets.metadata_snippet(
        tags=metadata.tags,
        annotation=metadata.annotation,
        version=metadata.version
    )


def format_workflow_builder(workflow: Workflow) -> str:
    metadata = workflow.metadata
    comment = '# WORKFLOW DECLARATION'
    section = snippets.workflow_builder_snippet(
        tag=workflow.tag_manager.get(workflow.get_uuid()),
        version=str(metadata.version),
        doc=metadata.annotation
    )
    return f'{comment}\n{section}\n'


def format_inputs(workflow: Workflow) -> str:
    out_str = '# INPUTS\n'
    for inp in workflow.inputs:
        uuid = inp.get_uuid()
        tag = workflow.tag_manager.get(uuid)
        if inp.is_galaxy_input_step:
            out_str += format_input(tag, inp)
    out_str += '\n'
    return out_str


def format_input(tag: str, inp: WorkflowInput) -> str:
    return snippets.workflow_input_snippet(
        tag=tag,
        datatype=inp.get_janis_datatype_str(),
        # TODO check whether defaults and values can appear here
        doc=format_docstring(inp)
    )


def format_docstring(entity: WorkflowStep | WorkflowInput | WorkflowOutput) -> Optional[str]:
    raw_doc = entity.get_docstring()
    if raw_doc:
        return raw_doc.replace('"', "'")
    return None


def format_outputs(workflow: Workflow) -> str:
    out_str = '# OUTPUTS\n'
    for out in workflow.outputs:
        uuid = out.get_uuid()
        tag = workflow.tag_manager.get(uuid)
        out_str += format_output(tag, out)
    out_str += '\n'
    return out_str


def format_output(tag: str, output: WorkflowOutput) -> str:
    return snippets.workflow_output_snippet(
        tag=tag,
        datatype=output.get_janis_datatype_str(),
        step_tag=output.step_tag,
        toolout_tag=output.toolout_tag
    )
    

def format_step(workflow: Workflow, step: WorkflowStep, step_count: int) -> str:
    tool_tag = step.tool.tag_manager.get(step.tool.get_uuid()) #type: ignore
    out_str: str = '\n'
    out_str += f'# step{step_count}: {tool_tag}\n'
    out_str += format_step_workflow_inputs(workflow, step)
    out_str += format_step_body(workflow, step)
    return out_str


def format_step_workflow_inputs(workflow: Workflow, step: WorkflowStep) -> str:
    # for step workflow inputs - get (tag, inp) 
    step_wflow_inputs = [inp for inp in workflow.inputs if inp.step_id == step.metadata.step_id]
    step_wflow_inputs = [(workflow.tag_manager.get(inp.get_uuid()), inp) for inp in step_wflow_inputs]
    step_wflow_inputs.sort(key=lambda x: x[0])
    out_str: str = ''
    for tag, inp in step_wflow_inputs:
        out_str += snippets.workflow_input_snippet(
            tag=tag,
            datatype=inp.get_janis_datatype_str(),
            doc=format_docstring(inp)
        )
    return out_str


def format_step_body(workflow: Workflow, step: WorkflowStep) -> str:
    step_tag = workflow.tag_manager.get(step.get_uuid())
    tool_tag = step.tool.tag_manager.get(step.tool.get_uuid()) #type: ignore
    linked_values = step.get_tool_tags_values()
    linked_values = format_linked_tool_values(linked_values, workflow)
    unlinked_values = step.get_unlinked_values()
    unlinked_values = format_unlinked_tool_values(unlinked_values, workflow)
    return snippets.workflow_step_snippet(
        tag=step_tag,
        tool=tool_tag,
        linked_values=linked_values,
        unlinked_values=unlinked_values, 
        doc=format_docstring(step)
    )


def format_linked_tool_values(tags_inputs: list[Tuple[str, InputValue]], workflow: Workflow, ignore_defaults: bool=True) -> list[Tuple[str, str]]:
    # provides the final list of tool input tags & values. 
    # logic for whether to write inputs if they are default, should wrap with quotes etc
    out: list[Tuple[str, str]] = []
    for comp_tag, input_value in tags_inputs:
        if input_value.is_default_value and ignore_defaults:
            pass
        else:
            formatted_value = format_value(input_value, workflow)
            out.append((comp_tag, formatted_value))
    return out


def format_unlinked_tool_values(unlinked_values: list[InputValue], workflow: Workflow) -> list[Tuple[str, str]]:
    # (gxvarname, text)
    out: list[Tuple[str, str]] = []
    for input_value in unlinked_values:
        tag = f'#UNKNOWN({input_value.gxparam.name})' if input_value.gxparam else '#UNKNOWN'
        formatted_value = format_value(input_value, workflow)
        out.append((tag, formatted_value))
    return out


def format_value(value: InputValue, workflow: Workflow) -> str:
    match value:
        case ConnectionInputValue():
            # get the step
            step = workflow.steps[value.step_id]
            assert(step.tool)
            # get the relevant tool output
            toolout = step.get_output(value.step_output).tool_output
            assert(toolout)
            # get their tags & format
            step_tag = workflow.tag_manager.get(step.get_uuid())
            toolout_tag = step.tool.tag_manager.get(toolout.get_uuid())
            text = f'w.{step_tag}.{toolout_tag}'
        case WorkflowInputInputValue():
            input_tag = workflow.tag_manager.get(value.input_uuid)
            text = f'w.{input_tag}'
        case StaticInputValue():
            text = f'{value.value}'
        case _:
            pass
    wrapped_value = wrap(text, value)
    return wrapped_value


def wrap(text: str, inval: InputValue) -> str:
    if should_quote(inval):
        return f'"{text}"'
    return text


def should_quote(inval: InputValue) -> bool:
    if isinstance(inval, StaticInputValue):
        quoted_types = [InputValueType.STRING, InputValueType.RUNTIME]
        if inval.valtype in quoted_types:
            return True
    return False
