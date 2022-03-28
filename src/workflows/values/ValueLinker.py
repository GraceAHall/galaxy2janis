



from typing import Any
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
            tag = component.get_janis_tag()
            strategy = select_linking_strategy(component, step, self.workflow)
            value = strategy.link()
            value = self.wrap_value(value, component)
            step.input_values[tag] = value

    def wrap_value(self, value: Any, component: CommandComponent) -> str:
        if self.should_quote(value, component):
            return f'"{value}"'
        return value

    def should_quote(self, value: Any, component: CommandComponent) -> bool:
        dclasses = set([x.classname for x in component.janis_datatypes])
        datatype_exclusions = ['Int', 'Float', 'Boolean']
        value_exclusions = [True, False, None]
        if any([x in dclasses for x in datatype_exclusions]): 
            return False
        elif value in value_exclusions:
            return False
        return True
