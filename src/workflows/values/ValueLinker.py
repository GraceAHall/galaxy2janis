



from command.components.CommandComponent import CommandComponent
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
            if self.is_linkable(component, step):
                self.link_component(component, step)

    def is_linkable(self, component: CommandComponent, step: ToolStep) -> bool:
        """
        checks whether a janis tool input can actually be linked to a value in the 
        galaxy workflow step.
        only possible if the component has a gxparam, and that gxparam is referenced as a the
        ConnectionStepInput, RuntimeStepInput or StaticStepInput
        """
        if component.gxparam:
            query = component.gxparam.name 
            if step.get_input(query):
                return True
        return False

    def link_component(self, component: CommandComponent, step: ToolStep) -> None:
        tag = component.get_janis_tag()
        step_input = step.get_input(component.gxparam.name)
        assert(step_input)
        strategy = select_linking_strategy(component, step_input, self.workflow)
        step.input_values[tag] = strategy.link()
    


