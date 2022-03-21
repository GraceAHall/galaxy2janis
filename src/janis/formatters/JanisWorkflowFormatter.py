


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

    def format_inputs(self, inputs: list[InputDataStep]) -> str:
        out_str = '# INPUTS\n'
        for inp in inputs:
            out_str += self.format_input(inp)
        out_str += '\n'
        return out_str

    def format_input(self, input: InputDataStep) -> str:
        return snippets.workflow_input_snippet(
            tag=input.get_janis_tag(),
            datatype=input.get_janis_datatype_str(),
            # TODO check whether defaults and values can appear here
            doc=input.get_docstring()
        )

    def format_steps(self, steps: list[ToolStep]) -> str:
        out_str = '# STEPS\n'
        for step in steps:
            out_str += self.format_step(step)
        out_str += '\n'
        return out_str
    
    def format_step(self, step: ToolStep) -> str:
        return snippets.workflow_step_snippet(
            tag=step.get_janis_tag(),
            tool=step.tool.metadata.id,
            tool_input_values=step.get_input_values(),
            doc=step.get_docstring()
        )
    
    def format_outputs(self, outputs: list[WorkflowOutput]) -> str:
        out_str = '# OUTPUTS\n'
        for out in outputs:
            out_str += self.format_output(out)
        out_str += '\n'
        return out_str

    def format_output(self, output: WorkflowOutput) -> str:
        return snippets.workflow_output_snippet(
            tag=output.name,
            datatype=output.datatype,
            source=output.source,
            output_name=output.output_name
        )

    def format_imports(self) -> str:
        return self.import_handler.imports_to_string()
        

