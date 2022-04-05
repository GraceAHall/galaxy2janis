
from typing import Any, Tuple
from janis.imports.WorkflowImportHandler import WorkflowImportHandler
import janis.snippets.workflow_snippets as snippets
from workflows.io.WorkflowInput import WorkflowInput
from workflows.io.WorkflowOutput import WorkflowOutput
from workflows.step.values.InputValue import InputValue, InputValueType
from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.Step import ToolStep

"""
Array?
UnionType?
"""

class JanisWorkflowFormatter:
    def __init__(self):
        self.import_handler = WorkflowImportHandler()
        self.include_inputs_with_default_value: bool = False 
        # TODO NOTE ^^^ SHOULD BE CLI RUNTIME SETTING

    def format_top_note(self, metadata: WorkflowMetadata) -> str:
        return snippets.gxtool2janis_note_snippet(
            workflow_name=metadata.name,
            workflow_version=metadata.version
        )

    def format_path_appends(self) -> str:
        return snippets.path_append_snippet()

    def format_metadata(self, metadata: WorkflowMetadata) -> str:
        return snippets.metadata_snippet(
            tags=metadata.tags,
            annotation=metadata.annotation,
            version=metadata.version
        )

    def format_workflow_builder(self, metadata: WorkflowMetadata) -> str:
        comment = '# WORKFLOW DECLARATION'
        section = snippets.workflow_builder_snippet(
            tag=metadata.name,
            version=str(metadata.version),
            doc=metadata.annotation
        )
        return f'{comment}\n{section}\n'

    def format_inputs(self, inputs: dict[str, WorkflowInput]) -> str:
        out_str = '# INPUTS\n'
        for tag, inp in inputs.items():
            if inp.from_input_step:
                out_str += self.format_input(tag, inp)
        out_str += '\n'
        return out_str

    def format_input(self, tag: str, inp: WorkflowInput) -> str:
        self.update_imports(tag, inp)
        return snippets.workflow_input_snippet(
            tag=tag,
            datatype=inp.get_janis_datatype_str(),
            # TODO check whether defaults and values can appear here
            doc=inp.get_docstring()
        )

    def format_steps(self, inputs: dict[str, WorkflowInput], steps: dict[str, ToolStep]) -> str:
        out_str = '# STEPS\n'
        for step_tag, step in steps.items():
            out_str += self.format_step(inputs, step_tag, step)
        out_str += '\n'
        return out_str
    
    def format_step(self, workflow_inputs: dict[str, WorkflowInput], step_tag: str, step: ToolStep) -> str:
        out_str: str = ''
        step_inputs = {tag: inp for tag, inp in workflow_inputs.items() if inp.step_id == step.metadata.step_id}
        for tag, inp in step_inputs.items():
            out_str += self.format_step_input(tag, inp)
        out_str += self.format_step_body(step_tag, step)
        return out_str

    def format_step_input(self, tag: str, inp: WorkflowInput) -> str:
        self.update_imports(tag, inp)
        return snippets.workflow_input_snippet(
            tag=tag,
            datatype=inp.get_janis_datatype_str(),
            # TODO check whether defaults and values can appear here
            doc=inp.get_docstring()
        )

    def format_step_body(self, tag: str, step: ToolStep) -> str:
        self.update_imports(tag, step)
        input_values = step.get_tool_tags_values()
        unlinked_values = step.get_unlinked_values()
        formatted_values = self.format_tool_values(input_values)
        return snippets.workflow_step_snippet(
            tag=tag, # TODO step tag formatter?
            tool=step.tool.metadata.id,
            tool_input_values=formatted_values,
            unlinked_values=unlinked_values,
            doc=step.get_docstring()
        )
    
    def format_tool_values(self, tags_inputs: dict[str, InputValue]) -> list[Tuple[str, str]]:
        # provides the final list of tool input tags & values. 
        # logic for whether to write inputs if they are default, should wrap with quotes etc
        out: list[Tuple[str, str]] = []
        for tag, input_value in tags_inputs.items():
            if input_value.is_default_value and not self.include_inputs_with_default_value:
                pass
            else:
                text_value = self.wrap_value(input_value)
                out.append((tag, text_value))
        return out

    def wrap_value(self, inval: InputValue) -> str:
        if self.should_quote(inval):
            return f'"{inval.value}"'
        return str(inval.value)

    def should_quote(self, inval: InputValue) -> bool:
        quoted_types = [InputValueType.STRING, InputValueType.RUNTIME]
        if inval.valtype in quoted_types:
            return True
        return False

    def format_outputs(self, outputs: dict[str, WorkflowOutput]) -> str:
        out_str = '# OUTPUTS\n'
        for tag, out in outputs.items():
            out_str += self.format_output(tag, out)
        out_str += '\n'
        return out_str

    def format_output(self, tag: str, output: WorkflowOutput) -> str:
        self.update_imports(tag, output)
        return snippets.workflow_output_snippet(
            tag=tag,  # TODO tag formatter?
            datatype=output.get_janis_datatype_str(),
            step_tag=output.step_tag,
            step_output=output.step_output
        )

    def update_imports(self, tag: str, component: Any) -> None:
        match component:
            case WorkflowInput():
                self.update_imports_for_workflow_input(component)
            case ToolStep():
                self.update_imports_for_tool_step(tag, component)
            case WorkflowOutput():
                self.update_imports_for_workflow_output(component)
            case _:
                pass
    
    def update_imports_for_workflow_input(self, inp: WorkflowInput) -> None:
        self.import_handler.update_datatype_imports(inp.janis_datatypes)
    
    def update_imports_for_tool_step(self, tool_tag: str, step: ToolStep) -> None:
        tool_path = step.get_definition_path()
        tool_path = tool_path.rsplit('.py')[0]
        tool_path = tool_path.replace('/', '.')
        self.import_handler.update_tool_imports(tool_path, tool_tag)
        for output in step.list_outputs():
            self.import_handler.update_datatype_imports(output.janis_datatypes)

    def update_imports_for_workflow_output(self, output: WorkflowOutput) -> None:
        self.import_handler.update_datatype_imports(output.janis_datatypes)

    def format_imports(self) -> str:
        return self.import_handler.imports_to_string()
        
