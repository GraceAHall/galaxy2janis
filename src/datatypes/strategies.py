


from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from entities.workflow.input import WorkflowInput
    from gx.command.components import Positional, Flag, Option
    from gx.command.components import OutputComponent
    from gx.gxtool.param.OutputParam import CollectionOutputParam

from abc import ABC, abstractmethod
import json

from datatypes.JanisDatatype import JanisDatatype
from .conversion import galaxy_to_janis
from . import core

import expressions


### SHARED FUNCTIONS ###

def types_from_param(entity: Positional | Option | OutputComponent) -> list[str]:
    if entity.gxparam and entity.gxparam.formats:
        return entity.gxparam.formats
    return []

def types_from_values(entity: Positional | Option) -> list[str]:
    values = entity.value_record.unique_values
    if values:
        if expressions.items_are_ints(values):
            return ['integer']
        elif expressions.items_are_floats(values):
            return ['float']
        elif not expressions.items_are_vars(values):
            return ['string']
    return []

def types_from_default(entity: Positional | Option) -> list[str]:
    if entity.default_value:
        if expressions.is_int(entity.default_value):
            return ['integer']
        elif expressions.is_float(entity.default_value):
            return ['float']
        elif not expressions.is_var(entity.default_value):
            return ['string']
    return []

def types_from_extension(output: OutputComponent) -> list[str]:
    if output.gxparam:
        if isinstance(output.gxparam, CollectionOutputParam):
            pattern: str = output.gxparam.discover_pattern # type: ignore
            compressed_types = ['gz', 'bz2']
            p_split = pattern.split('.')
            while p_split[-1] in compressed_types:
                p_split = p_split[:-1]
            ext = p_split[-1]
            return [f'.{ext}']
    return []


### STRATEGIES ###

class DatatypeGetStrategy(ABC):
    @abstractmethod
    def get(self, entity: Any) -> list[JanisDatatype]:
        """parses an entity to return the janis datatype(s)"""
        ...

class PositionalStrategy(DatatypeGetStrategy):
    def get(self, entity: Positional) -> list[JanisDatatype]:
        gxtypes = types_from_param(entity)
        if not gxtypes:
            gxtypes = types_from_values(entity)
        if not gxtypes:
            gxtypes = types_from_default(entity)
        if not gxtypes:
            gxtypes = []
        return galaxy_to_janis(gxtypes)

class FlagStrategy(DatatypeGetStrategy):
    def get(self, entity: Flag) -> list[JanisDatatype]:
        return [core.bool_t]

class OptionStrategy(DatatypeGetStrategy):
    def get(self, entity: Option) -> list[JanisDatatype]:
        gxtypes = types_from_param(entity)
        if not gxtypes:
            gxtypes = types_from_values(entity)
        if not gxtypes:
            gxtypes = types_from_default(entity)
        if not gxtypes:
            gxtypes = []
        return galaxy_to_janis(gxtypes)

class OutputStrategy(DatatypeGetStrategy):
    def get(self, entity: OutputComponent) -> list[JanisDatatype]:
        gxtypes = types_from_param(entity)
        if not gxtypes:
            gxtypes = types_from_extension(entity)
        if not gxtypes:
            gxtypes = []
        return galaxy_to_janis(gxtypes)

class WorkflowInputStrategy(DatatypeGetStrategy):
    def get(self, entity: WorkflowInput) -> list[JanisDatatype]:
        return [entity.datatype]

class GalaxyInputStepStrategy(DatatypeGetStrategy):
    def get(self, entity: dict[str, Any]) -> list[JanisDatatype]:
        tool_state = json.loads(entity['tool_state'])
        if 'format' in tool_state:
            return galaxy_to_janis(tool_state['format'])
        else:
            return [core.file_t]



# these are the entities which we can get a datatype for

strategy_map = {
    'Positional': PositionalStrategy,
    'Flag': FlagStrategy,
    'Option': OptionStrategy,
    'RedirectOutput': OutputStrategy,
    'InputOutput': OutputStrategy,
    'WildcardOutput': OutputStrategy,
    'GalaxyInputStep': GalaxyInputStepStrategy,
    'WorkflowInput': WorkflowInputStrategy,
}





        
