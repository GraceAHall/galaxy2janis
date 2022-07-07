

from typing import Any, Optional
from datatypes import JanisDatatype

from .core import DEFAULT_DATATYPE
from .strategies import strategy_map
from .conversion import janis_to_core


def get(entity: Any, entity_type: Optional[str]=None, source: str='galaxy') -> list[JanisDatatype]:
    etype = entity_type if entity_type else entity.__class__.__name__
    strategy = strategy_map[etype] 
    jtypes = strategy().get(entity)
    core_types = janis_to_core(jtypes)
    if core_types:
        return core_types
    else:
        return [DEFAULT_DATATYPE]

    

