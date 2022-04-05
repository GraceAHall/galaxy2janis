

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from command.components.CommandComponent import CommandComponent
from workflows.workflow.Workflow import Workflow
from workflows.step.values.InputValue import InputValue, InputValueType
from workflows.step.values.value_types import select_input_value_type
from workflows.step.inputs.StepInput import (
    ConnectionStepInput,
    StaticStepInput
)
from xmltool.param.Param import Param

@dataclass
class LinkingStrategy(ABC):
    component: CommandComponent

    def link(self) -> InputValue:
        return InputValue(
            value=str(self.get_value()),
            valtype=self.get_valtype(),
            comptype=self.get_comptype(),
            gxparam=self.get_gxparam()
        )

    @abstractmethod
    def get_value(self) -> Any:
        ...
    
    @abstractmethod
    def get_valtype(self) -> InputValueType:
        ...

    @abstractmethod
    def get_gxparam(self) -> Optional[Param]:
        ...
    
    def get_comptype(self) -> str:
        return type(self.component).__name__.lower() 


@dataclass
class ConnectionLinkingStrategy(LinkingStrategy):
    step_input: ConnectionStepInput
    workflow: Workflow
    
    def get_value(self) -> Any:
        step_id = self.step_input.step_id
        step_tag = self.workflow.get_step_tag_by_step_id(step_id)
        step_output = self.step_input.output_name
        return f'w.{step_tag}.{step_output}'
    
    def get_valtype(self) -> InputValueType:
        return InputValueType.CONNECTION
    
    def get_gxparam(self) -> Optional[Param]:
        return self.step_input.gxparam
    

@dataclass
class RuntimeLinkingStrategy(LinkingStrategy):

    def get_value(self) -> Any:
        return 'RuntimeValue'
    
    def get_valtype(self) -> InputValueType:
        return InputValueType.RUNTIME
    
    def get_gxparam(self) -> Optional[Param]:
        return self.component.gxparam
    

@dataclass
class StaticValueLinkingStrategy(LinkingStrategy):
    step_input: StaticStepInput
    value_translations = {
        'false': False,
        'False': False,
        'true': True,
        'True': True,
        'null': None,
        'none': None,
        'None': None,
        '""': None,
        "''": None
    }

    def get_value(self) -> Any:
        gx_value = self.step_input.value
        value = self.standardise_value(gx_value)
        return value

    def standardise_value(self, value: Any) -> Any:
        if value in self.value_translations:
            return self.value_translations[value]
        return value
    
    def get_valtype(self) -> InputValueType:
        value = self.get_value()
        if value == 'RuntimeValue':
            return InputValueType.RUNTIME
        else:
            return select_input_value_type(self.component, value)
    
    def get_gxparam(self) -> Optional[Param]:
        return self.step_input.gxparam
    

@dataclass
class DefaultValueLinkingStrategy(LinkingStrategy):

    def get_value(self) -> Any:
        return self.component.get_default_value()
    
    def get_valtype(self) -> InputValueType:
        return select_input_value_type(self.component, self.get_value())

    def get_gxparam(self) -> Optional[Param]:
        return self.component.gxparam