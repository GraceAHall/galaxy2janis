

from typing import Any
from datatypes import JanisDatatype

from .core import file_t
from .core import CORE_DATATYPES
from .core import DEFAULT_DATATYPE

from .register import register
from .strategies import strategy_map


def get_datatype(entity: Any, source: str='galaxy') -> list[JanisDatatype]:
    # TODO future: allow source to cover cwl, wdl, nextflow.
    # strategy will change depending on the entity and the source 
    # (eg toolinput from nextflow, workflow output from cwl etc)
    galaxy_types = parse_datatype(entity)
    janis_types = map_to_janis(galaxy_types)
    core_types = map_to_core(janis_types)
    if core_types:
        return core_types
    else:
        return [DEFAULT_DATATYPE]

def parse_datatype(entity: Any) -> list[str]:
    entity_type = entity.__class__.__name__
    strategy = strategy_map[entity_type] 
    galaxy_types = strategy(entity)
    return galaxy_types

def map_to_janis(galaxy_types: list[str]) -> list[JanisDatatype]:
    out: list[JanisDatatype] = []
    for gtype in galaxy_types:
        jtype = register.get(gtype)
        if jtype is not None:
            out.append(jtype)
    return out

def map_to_core(query_types: list[JanisDatatype]) -> list[JanisDatatype]:
    core: dict[str, JanisDatatype] = {} # dict to keep unique
    for qtype in query_types:
        if qtype.classname not in CORE_DATATYPES:
            core[file_t.classname] = file_t # cast to file type 
    return list(core.values()) # return core types

