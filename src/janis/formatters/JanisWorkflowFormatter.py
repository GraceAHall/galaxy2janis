
from typing import Any
from janis.imports.WorkflowImportHandler import WorkflowImportHandler
import janis.snippets.workflow_snippets as snippets
from workflows.io.Output import WorkflowOutput
from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.Step import InputDataStep, ToolStep

"""
Array?
UnionType?
"""

class JanisWorkflowFormatter:
    def __init__(self):
        self.import_handler = WorkflowImportHandler()

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

    def format_inputs(self, inputs: dict[str, InputDataStep]) -> str:
        out_str = '# INPUTS\n'
        for name, inp in inputs.items():
            out_str += self.format_input(name, inp)
        out_str += '\n'
        return out_str

    def format_input(self, name: str, step: InputDataStep) -> str:
        self.update_imports(name, step)
        return snippets.workflow_input_snippet(
            tag=name, # TODO tag formatter
            datatype=step.get_janis_datatype_str(),
            # TODO check whether defaults and values can appear here
            doc=step.get_docstring()
        )

    def format_steps(self, steps: dict[str, ToolStep]) -> str:
        out_str = '# STEPS\n'
        for name, step in steps.items():
            out_str += self.format_step(name, step)
        out_str += '\n'
        return out_str
    
    def format_step(self, name: str, step: ToolStep) -> str:
        self.update_imports(name, step)
        return snippets.workflow_step_snippet(
            tag=name, # TODO tag formatter
            tool=step.tool.metadata.id,
            tool_input_values=step.input_values,
            doc=step.get_docstring()
        )

    def format_outputs(self, outputs: dict[str, WorkflowOutput]) -> str:
        out_str = '# OUTPUTS\n'
        for name, out in outputs.items():
            out_str += self.format_output(name, out)
        out_str += '\n'
        return out_str

    def format_output(self, name: str, output: WorkflowOutput) -> str:
        self.update_imports(name, output)
        return snippets.workflow_output_snippet(
            tag=name,  # TODO tag formatter?
            datatype=output.get_janis_datatype_str(),
            source_step=output.source_step,
            source_tag=output.source_tag
        )

    def update_imports(self, name: str, component: Any) -> None:
        match component:
            case InputDataStep():
                self.update_imports_for_input_data(component)
            case ToolStep():
                self.update_imports_for_tool_step(name, component)
            case WorkflowOutput():
                self.update_imports_for_workflow_output(component)
            case _:
                pass
    
    def update_imports_for_input_data(self, step: InputDataStep) -> None:
        for output in step.outputs:
            self.import_handler.update_datatype_imports(output.janis_datatypes)
    
    def update_imports_for_tool_step(self, name: str, step: ToolStep) -> None:
        tool_path = step.get_definition_path()
        tool_path = tool_path.rsplit('.py')[0]
        tool_path = tool_path.replace('/', '.')
        tool_name = step.tool.metadata.id
        self.import_handler.update_tool_imports(tool_path, tool_name)
        for output in step.outputs:
            self.import_handler.update_datatype_imports(output.janis_datatypes)

    def update_imports_for_workflow_output(self, output: WorkflowOutput) -> None:
        self.import_handler.update_datatype_imports(output.janis_datatypes)

    def format_imports(self) -> str:
        return self.import_handler.imports_to_string()
        
