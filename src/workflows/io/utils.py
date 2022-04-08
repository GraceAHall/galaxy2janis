


from workflows.io.WorkflowInput import WorkflowInput
from workflows.step.WorkflowStep import InputDataStep
from workflows.step.outputs.StepOutput import StepOutput



def create_input_from_step(step: InputDataStep, out: StepOutput) -> WorkflowInput:
    raise NotImplementedError()

def create_output_from_step(step: InputDataStep, out: StepOutput) -> WorkflowInput:
    raise NotImplementedError()
