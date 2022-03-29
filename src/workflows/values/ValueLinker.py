



from workflows.step.Step import ToolStep
from workflows.values.LinkingStrategy import select_linking_strategy
from workflows.workflow.Workflow import Workflow


class ValueLinker:
    def __init__(self, workflow: Workflow):
        self.workflow = workflow

    def link(self) -> None:
        steps = self.workflow.steps.values()
        for step in steps:
            self.link_step(step)

    def link_step(self, step: ToolStep) -> None:
        assert(step.tool)
        for component in step.tool.get_inputs():
            tag = component.get_janis_tag()
            strategy = select_linking_strategy(component, step, self.workflow)
            step.input_values[tag] = strategy.link()
    


