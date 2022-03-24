


from janis.imports.ImportHandler import ImportHandler
import janis.snippets.workflow_snippets as snippets
from workflows.io.Output import WorkflowOutput
from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.Step import InputDataStep, ToolStep


class JanisWorkflowFormatter:
    def __init__(self):
        self.import_handler = ImportHandler()

    def format_path_appends(self) -> str:
        return snippets.path_append_snippet()

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

    def format_input(self, name: str, input: InputDataStep) -> str:
        return snippets.workflow_input_snippet(
            tag=name, # TODO tag formatter
            datatype=input.get_janis_datatype_str(),
            # TODO check whether defaults and values can appear here
            doc=input.get_docstring()
        )

    def format_steps(self, steps: dict[str, ToolStep]) -> str:
        out_str = '# STEPS\n'
        for name, step in steps.items():
            out_str += self.format_step(name, step)
        out_str += '\n'
        return out_str
    
    def format_step(self, name: str, step: ToolStep) -> str:
        return snippets.workflow_step_snippet(
            tag=name, # TODO tag formatter
            tool=step.tool.metadata.id,
            tool_input_values=step.get_input_values(),
            doc=step.get_docstring()
        )
    
    def format_outputs(self, outputs: dict[str, WorkflowOutput]) -> str:
        out_str = '# OUTPUTS\n'
        for name, out in outputs.items():
            out_str += self.format_output(name, out)
        out_str += '\n'
        return out_str

    def format_output(self, name: str, output: WorkflowOutput) -> str:
        return snippets.workflow_output_snippet(
            tag=name,  # TODO tag formatter
            datatype=output.datatype,
            source=output.source
        )

    def format_imports(self) -> str:
        return self.import_handler.imports_to_string()
        

