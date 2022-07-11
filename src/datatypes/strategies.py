
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
from datatypes.JanisDatatype import JanisDatatype

from shellparser.components.outputs.OutputComponent import OutputComponent
from .conversion import galaxy_to_janis
from . import core

if TYPE_CHECKING:
    from shellparser.components.inputs import Positional, Flag, Option
    from entities.workflow import WorkflowInput
    from entities.workflow import WorkflowOutput
    from entities.workflow import StepInput
    from entities.workflow import StepOutput


class DatatypeGetStrategy(ABC):

    @abstractmethod
    def get(self, entity: Any) -> list[JanisDatatype]:
        """parses an entity to return the janis datatype(s)"""
        ...


class PositionalStrategy(DatatypeGetStrategy):
    def get(self, entity: Positional) -> list[JanisDatatype]:
        gxtypes: list[str] = []
        if entity.gxparam:
            gxtypes = entity.gxparam.datatypes
        elif entity.value_record.values_are_ints():
            gxtypes = ['integer']
        elif entity.value_record.values_are_floats():
            gxtypes = ['float']
        return galaxy_to_janis(gxtypes)

class FlagStrategy(DatatypeGetStrategy):
    def get(self, entity: Flag) -> list[JanisDatatype]:
        return [core.bool_t]

class OptionStrategy(DatatypeGetStrategy):
    def get(self, entity: Option) -> list[JanisDatatype]:
        gxtypes: list[str] = []
        if entity.gxparam:
            gxtypes = entity.gxparam.datatypes
        elif entity.value_record.values_are_ints(): # TODO bad
            gxtypes = ['integer']
        elif entity.value_record.values_are_floats():
            gxtypes = ['float']
        return galaxy_to_janis(gxtypes)

class OutputStrategy(DatatypeGetStrategy):
    def get(self, entity: OutputComponent) -> list[JanisDatatype]:
        gxtypes: list[str] = []
        if entity.gxparam:
            gxtypes = entity.gxparam.datatypes
        return galaxy_to_janis(gxtypes)

class StepInputStrategy(DatatypeGetStrategy):
    def get(self, entity: StepInput) -> list[JanisDatatype]:
        return galaxy_to_janis(entity.gxparam.datatypes)

class StepOutputStrategy(DatatypeGetStrategy):
    def get(self, entity: StepOutput) -> list[JanisDatatype]:
        return entity.janis_datatypes

class GalaxyStepOutputStrategy(DatatypeGetStrategy):
    def get(self, entity: dict[str, Any]) -> list[JanisDatatype]:
        gxtypes = entity['type'].split(',')
        return galaxy_to_janis(gxtypes)

class WorkflowInputStrategy(DatatypeGetStrategy):
    def get(self, entity: WorkflowInput) -> list[JanisDatatype]:
        if entity.janis_datatypes:
            return entity.janis_datatypes
        elif entity.gx_datatypes:
            return galaxy_to_janis(entity.gx_datatypes)
        else:
            raise RuntimeError

class WorkflowOutputStrategy(DatatypeGetStrategy):
    def get(self, entity: WorkflowOutput) -> list[JanisDatatype]:
        return entity.janis_datatypes


strategy_map = {
    'Positional': PositionalStrategy,
    'Flag': FlagStrategy,
    'Option': OptionStrategy,
    'RedirectOutput': OutputStrategy,
    'InputOutput': OutputStrategy,
    'WildcardOutput': OutputStrategy,
    'UncertainOutput': OutputStrategy,
    'StepInput':StepInputStrategy,
    'StepOutput': StepOutputStrategy,
    'GalaxyStepOutput': GalaxyStepOutputStrategy,
    'WorkflowInput': WorkflowInputStrategy,
    'WorkflowOutput': WorkflowOutputStrategy,
}





        
