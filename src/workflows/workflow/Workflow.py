

from dataclasses import dataclass

from janis.formatters.JanisWorkflowFormatter import JanisWorkflowFormatter
from workflows.step.StepInput import ConnectionStepInput, StaticStepInput, UserDefinedStepInput

from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.Step import InputDataStep, ToolStep
from workflows.io.Output import WorkflowOutput


@dataclass
class Workflow:
    metadata: WorkflowMetadata
    steps: dict[str, ToolStep]
    inputs: dict[str, InputDataStep]
    outputs: dict[str, WorkflowOutput]

    def assign_step_values(self) -> None:
        for step in self.steps.values():
            if step.tool:
                for component in step.tool.get_inputs():
                    name = component.get_janis_tag()
                    # has galaxy value we can link to step details
                    if component.gxparam:
                        varname = component.gxparam.name
                        step_input = step.get_input(varname)
                        match step_input:
                            case ConnectionStepInput():
                                tag = self.get_step_tag_by_id(step_input.step_id)
                                output = step_input.output_name
                                value = f'w.{tag}.{output}'
                            case UserDefinedStepInput():
                                value = 'RUNTIMEVALUE'
                            case StaticStepInput():
                                value = step_input.value
                            case _:
                                pass
                    # no galaxy variable
                    else:
                        value = component.get_default_value()
                    step.input_values.append((name, value))

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
        return str_note + str_path + str_metadata + str_imports + str_builder + str_inputs + str_steps + str_outputs
