

from abc import ABC, abstractmethod
from typing import Any

from command.components.CommandComponent import CommandComponent
from workflows.workflow.Workflow import Workflow
from workflows.step.Step import ToolStep
from workflows.values.InputValue import InputValue, InputValueType
from workflows.values.value_types import select_input_value_type
from workflows.step.StepInput import (
    ConnectionStepInput,
    RuntimeStepInput,
    StaticStepInput
)


class LinkingStrategy(ABC):

    def link(self) -> InputValue:
        valtype = self.get_valtype()
        value = self.get_value()
        return InputValue(
            valtype=valtype,
            value=str(value)
        )
    
    @abstractmethod
    def get_value(self) -> Any:
        ...
    
    @abstractmethod
    def get_valtype(self) -> InputValueType:
        ...
    

class ConnectionLinkingStrategy(LinkingStrategy):
    def __init__(self, component: CommandComponent, step_input: ConnectionStepInput, workflow: Workflow):
        self.component = component
        self.step_input = step_input
        self.workflow = workflow

    def get_value(self) -> str:
        source_id = self.step_input.step_id
        source_tag = self.workflow.get_step_tag_by_id(source_id)
        source_output = self.step_input.output_name
        return f'w.{source_tag}.{source_output}'
    
    def get_valtype(self) -> InputValueType:
        return InputValueType.CONNECTION


class RuntimeLinkingStrategy(LinkingStrategy):

    def get_value(self) -> str:
        return 'RuntimeValue'
    
    def get_valtype(self) -> InputValueType:
        return InputValueType.RUNTIME_VALUE


class StaticValueLinkingStrategy(LinkingStrategy):
    value_translations = {
        'false': False,
        'False': False,
        'true': True,
        'True': True,
        'null': None
    }

    def __init__(self, component: CommandComponent, step_input: StaticStepInput):
        self.component = component
        self.step_input = step_input

    def get_value(self) -> Any:
        gx_value = self.step_input.value
        value = self.standardise_value(gx_value)
        return value

    def standardise_value(self, value: Any) -> Any:
        if value in self.value_translations:
            return self.value_translations[value]
        return value
    
    def get_valtype(self) -> InputValueType:
        return select_input_value_type(self.component, self.get_value())


class DefaultValueLinkingStrategy(LinkingStrategy):
    def __init__(self, component: CommandComponent):
        self.component = component

    def get_value(self) -> Any:
        return self.component.get_default_value()
    
    def get_valtype(self) -> InputValueType:
        return select_input_value_type(self.component, self.get_value())



def select_linking_strategy(component: CommandComponent, step: ToolStep, workflow: Workflow) -> LinkingStrategy:
    if component.gxparam:
        query = component.gxparam.name
        step_input = step.get_input(query)
        if step_input:
            match step_input:
                case ConnectionStepInput():
                    return ConnectionLinkingStrategy(component, step_input, workflow)
                case RuntimeStepInput():
                    return RuntimeLinkingStrategy() 
                case StaticStepInput():
                    return StaticValueLinkingStrategy(component, step_input)
                case _:
                    return RuntimeLinkingStrategy()
    return DefaultValueLinkingStrategy(component)
    