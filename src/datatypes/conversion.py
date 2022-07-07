


from datatypes import JanisDatatype

from .core import file_t
from .core import CORE_DATATYPES
from .register import register



def galaxy_to_janis(galaxy_types: list[str]) -> list[JanisDatatype]:
    out: list[JanisDatatype] = []
    for gtype in galaxy_types:
        jtype = register.get(gtype)
        if jtype is not None:
            out.append(jtype)
    return out

def janis_to_core(query_types: list[JanisDatatype]) -> list[JanisDatatype]:
    core: dict[str, JanisDatatype] = {} # dict to keep unique
    for qtype in query_types:
        if qtype.classname not in CORE_DATATYPES:
            core[file_t.classname] = file_t # cast to file type 
    return list(core.values()) # return core types

