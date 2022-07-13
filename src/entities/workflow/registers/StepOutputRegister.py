


from ..step.outputs import StepOutput
import tags


class StepOutputRegister:
    def __init__(self):
        self.register: list[StepOutput] = []

    def add(self, step_output: StepOutput) -> None:
        tags.workflow.register(step_output)
        self.register.append(step_output)

    def list(self) -> list[StepOutput]:
        return self.register
        

