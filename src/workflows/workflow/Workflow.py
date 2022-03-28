

from dataclasses import dataclass

from janis.formatters.JanisWorkflowFormatter import JanisWorkflowFormatter
from workflows.step.StepInput import ConnectionStepInput, StaticStepInput, RuntimeStepInput

from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.Step import InputDataStep, ToolStep
from workflows.io.Output import WorkflowOutput


@dataclass
class Workflow:
    metadata: WorkflowMetadata
    steps: dict[str, ToolStep]
    inputs: dict[str, InputDataStep]
    outputs: dict[str, WorkflowOutput]

    def get_step_tag_by_id(self, query_id: int) -> str:
        # check input steps
        for tag, step in self.inputs.items():
            if step.metadata.step_id == query_id:
                return tag
        # check tool steps
        for tag, step in self.steps.items():
            if step.metadata.step_id == query_id:
                return tag
        raise RuntimeError(f'no step with step_id={query_id}')

    def assign_tool_definition_paths(self, tools_dir: str) -> None:
        for tag, step in self.steps.items():
            path = f'{tools_dir}/{tag}/{tag}.py'
            step.set_definition_path(path)

    def to_janis_definition(self) -> str:
        formatter = JanisWorkflowFormatter()
        str_note = formatter.format_top_note(self.metadata)
        str_path = formatter.format_path_appends()
        str_metadata = formatter.format_metadata(self.metadata)
        str_builder = formatter.format_workflow_builder(self.metadata)
        str_inputs = formatter.format_inputs(self.inputs)
        str_steps = formatter.format_steps(self.steps)
        str_outputs = formatter.format_outputs(self.outputs)
        str_imports = formatter.format_imports()
        return str_note + str_path + str_imports + str_metadata + str_builder + str_inputs + str_steps + str_outputs
