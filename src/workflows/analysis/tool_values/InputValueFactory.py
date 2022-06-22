

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from gx.xmltool.param.Param import Param
from shellparser.components.CommandComponent import CommandComponent

from entities.workflow.workflow import Workflow
from entities.workflow.input import WorkflowInput
from entities.workflow.step.tool_values import (
    InputValue, 
    ConnectionInputValue, 
    RuntimeInputValue, 
    StaticInputValue, 
    DefaultInputValue,
    InputValueType,
    WorkflowInputInputValue
)
from workflows.analysis.tool_values.utils import select_input_value_type
from entities.workflow.step.inputs import ConnectionStepInput


@dataclass
class InputValueFactory(ABC):
    component: CommandComponent

    @abstractmethod
    def create(self) -> InputValue:
        ...
        
    def get_comptype(self) -> str:
        return type(self.component).__name__.lower() 


@dataclass
class ConnectionInputValueFactory(InputValueFactory):
    step_input: ConnectionStepInput
    workflow: Workflow

    def create(self) -> ConnectionInputValue:
        return ConnectionInputValue(
            step_id=self.step_input.step_id,
            step_output=self.step_input.output_name,
            comptype=self.get_comptype(),
            gxparam=self.step_input.gxparam
        )
    

@dataclass
class RuntimeInputValueFactory(InputValueFactory):

    def create(self) -> RuntimeInputValue:
        return RuntimeInputValue(
            comptype=self.get_comptype(),
            gxparam=self.component.gxparam
        )
    

@dataclass
class StaticInputValueFactory(InputValueFactory):
    value: Any
    
    def create(self) -> StaticInputValue:
        return StaticInputValue(
            value=self.value,
            valtype=self.get_valtype(),
            comptype=self.get_comptype(),
            gxparam=self.component.gxparam
        )

    def get_valtype(self) -> InputValueType:
        return select_input_value_type(self.component, self.value)


@dataclass
class DefaultInputValueFactory(InputValueFactory):
    
    def create(self) -> DefaultInputValue:
        value = DefaultInputValue(
            value=self.get_value(),
            valtype=self.get_valtype(),
            comptype=self.get_comptype(),
            gxparam=self.component.gxparam
        )
        value.is_default_value = True
        return value

    def get_value(self) -> Any:
        return self.component.default_value
    
    def get_valtype(self) -> InputValueType:
        return select_input_value_type(self.component, self.get_value())

    def get_gxparam(self) -> Optional[Param]:
        return self.component.gxparam

@dataclass
class WorkflowInputInputValueFactory(InputValueFactory):
    workflow_input: WorkflowInput
    
    def create(self) -> WorkflowInputInputValue:
        return WorkflowInputInputValue(
            input_uuid=self.workflow_input.uuid,
            comptype=self.get_comptype(),
            gxparam=self.component.gxparam
        )