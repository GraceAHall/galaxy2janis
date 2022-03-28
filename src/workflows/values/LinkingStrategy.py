

from abc import ABC, abstractmethod
from typing import Any

from command.components.CommandComponent import CommandComponent
from workflows.workflow.Workflow import Workflow
from workflows.step.Step import ToolStep
from workflows.step.StepInput import (
    ConnectionStepInput,
    RuntimeStepInput,
    StaticStepInput,
    StepInput
)


class LinkingStrategy(ABC):
    @abstractmethod
    def link(self) -> Any:
        ...

class ConnectionLinkingStrategy(LinkingStrategy):
    def __init__(self, component: CommandComponent, step_input: ConnectionStepInput, workflow: Workflow):
        self.component = component
        self.step_input = step_input
        self.workflow = workflow

    def link(self) -> Any:
        source_id = self.step_input.step_id
        source_tag = self.workflow.get_step_tag_by_id(source_id)
        source_output = self.step_input.output_name
        return f'w.{source_tag}.{source_output}'


class RuntimeLinkingStrategy(LinkingStrategy):
    def link(self) -> Any:
        return 'RUNTIMEVALUE'


class StaticValueLinkingStrategy(LinkingStrategy):
    value_translations = {
        'false': False,
        'False': False,
        'true': True,
        'True': True,
        'null': None
    }

    def __init__(self, step_input: StaticStepInput):
        self.step_input = step_input

    def link(self) -> Any:
        gx_value = self.step_input.value
        sanitised_value = self.sanitise(gx_value)
        return sanitised_value

    def sanitise(self, value: Any) -> str:
        if value in self.value_translations:
            return str(self.value_translations[value])
        return value


class DefaultValueLinkingStrategy(LinkingStrategy):
    def __init__(self, component: CommandComponent):
        self.component = component

    def link(self) -> Any:
        return self.component.get_default_value()


def select_linking_strategy(component: CommandComponent, step: ToolStep, workflow: Workflow) -> LinkingStrategy:
    if component.gxparam:
        query = component.gxparam.name
        step_input = step.get_input(query)
        match step_input:
            case ConnectionStepInput():
                return ConnectionLinkingStrategy(component, step_input, workflow)
            case RuntimeStepInput():
                return RuntimeLinkingStrategy() 
            case StaticStepInput():
                return StaticValueLinkingStrategy(step_input)
            case _:
                return RuntimeLinkingStrategy()
    return DefaultValueLinkingStrategy(component)
    