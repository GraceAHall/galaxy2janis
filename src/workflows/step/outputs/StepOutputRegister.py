



from workflows.step.outputs.StepOutput import StepOutput


class StepOutputRegister:
    def __init__(self, step_outputs: list[StepOutput]):
        self.register = step_outputs

    def get(self, gxvarname: str) -> StepOutput:
        for output in self.register:
            if output.gxvarname == gxvarname:
                return output
        raise RuntimeError(f'could not find output {gxvarname}')

    def list_outputs(self) -> list[StepOutput]:
        return self.register




