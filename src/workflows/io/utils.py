


from workflows.io.WorkflowInput import WorkflowInput
from workflows.step.Step import InputDataStep
from workflows.step.outputs.StepOutput import StepOutput



def create_input_from_step(step: InputDataStep, out: StepOutput) -> WorkflowInput:
    raise NotImplementedError()

def create_output_from_step(step: InputDataStep, out: StepOutput) -> WorkflowInput:
    raise NotImplementedError()
    # def get_outputs(self) -> dict[str, WorkflowOutput]:
    #     out: dict[str, WorkflowOutput] = {}
    #     tool_steps = self.get_tool_steps()

    #     for step_tag, step in tool_steps.items():
    #         for workflow_out in step.metadata.workflow_outputs:
    #             step_output = step.get_step_output(workflow_out['output_name'])
    #             assert(step_output)
    #             output = WorkflowOutput( 
    #                 source_step=step_tag,
    #                 source_tag=step_output.name,
    #                 gx_datatypes=step_output.gx_datatypes
    #             )
    #             name = f'{step.get_tool_name()}_{workflow_out["output_name"]}'
    #             output_tag = self.tag_formatter.format(name)
    #             self.datatype_annotator.annotate(output)
    #             out[output_tag] = output
    #     return out