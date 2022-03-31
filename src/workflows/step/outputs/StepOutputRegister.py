



from workflows.step.outputs.StepOutput import StepOutput


class StepOutputRegister:
    def __init__(self, step_outputs: list[StepOutput]):
        self.register = step_outputs

    def get(self, query_name: str) -> StepOutput:
        for output in self.register:
            if output.name == query_name:
                return output
        raise RuntimeError(f'could not find output {query_name}')

    def list_outputs(self) -> list[StepOutput]:
        return self.register




