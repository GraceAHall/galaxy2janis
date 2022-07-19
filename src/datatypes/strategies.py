


from __future__ import annotations
from abc import ABC, abstractmethod
import json
from typing import TYPE_CHECKING, Any

from datatypes.JanisDatatype import JanisDatatype
from .conversion import galaxy_to_janis
from . import core

if TYPE_CHECKING:
    from entities.workflow.input import WorkflowInput
    from gx.command.components import Positional, Flag, Option
    from gx.command.components import OutputComponent
    from gx.gxtool.param.OutputParam import CollectionOutputParam


class DatatypeGetStrategy(ABC):

    @abstractmethod
    def get(self, entity: Any) -> list[JanisDatatype]:
        """parses an entity to return the janis datatype(s)"""
        ...


class PositionalStrategy(DatatypeGetStrategy):
    def get(self, entity: Positional) -> list[JanisDatatype]:
        gxtypes: list[str] = []
        if entity.gxparam:
            gxtypes = entity.gxparam.formats
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
            gxtypes = entity.gxparam.formats
        elif entity.value_record.values_are_ints(): # TODO bad
            gxtypes = ['integer']
        elif entity.value_record.values_are_floats():
            gxtypes = ['float']
        return galaxy_to_janis(gxtypes)

class OutputStrategy(DatatypeGetStrategy):
    def get(self, entity: OutputComponent) -> list[JanisDatatype]:
        gxtypes: list[str] = []
        if entity.gxparam and entity.gxparam.formats:
            gxtypes = entity.gxparam.formats
        elif entity.gxparam and isinstance(entity.gxparam, CollectionOutputParam):
            ext = self.extract_extension(entity.gxparam.discover_pattern)
            gxtypes = [ext]
        return galaxy_to_janis(gxtypes)

    def extract_extension(self, pattern: str) -> str:
        compressed_types = ['gz', 'bz2']
        p_split = pattern.split('.')
        while p_split[-1] in compressed_types:
            p_split = p_split[:-1]
        ext = p_split[-1]
        return f'.{ext}'

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





        
