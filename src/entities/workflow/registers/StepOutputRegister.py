



from entities.workflow import StepOutput


class StepOutputRegister:
    def __init__(self):
        self.register: list[StepOutput] = []

    def add(self, step_output: StepOutput) -> None:
        self.register.append(step_output)

    def list(self) -> list[StepOutput]:
        return self.register
        
    # def get(self, gxvarname: str) -> StepOutput:
    #     raise RuntimeError(f'could not find output {gxvarname}')
    #     for output in self.register:
    #         if output.gx_varname == gxvarname:
    #             return output
    

