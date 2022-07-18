

from typing import Any, Optional, Protocol
from datatypes import JanisDatatype

from .strategies import strategy_map
from .conversion import janis_to_core
from .conversion import select_primary_core_type


def get(entity: Any, entity_type: Optional[str]=None, source: str='galaxy') -> JanisDatatype:
    etype = entity_type if entity_type else entity.__class__.__name__
    strategy = strategy_map[etype] 
    jtypes = strategy().get(entity)
    core_types = janis_to_core(jtypes)
    return select_primary_core_type(core_types)


class FormattableEntity(Protocol):
    @property
    def optional(self) -> bool:
        ...

    @property
    def array(self) -> bool:
        ...

def get_str(entity: FormattableEntity) -> str:
    jtype = get(entity=entity)
    
    if not entity.optional and not entity.array: # not array not optional
        out_str = f'{jtype.classname}'
    
    elif not entity.optional and entity.array: # array and not optional
        out_str = f'Array({jtype.classname})'
    
    elif entity.optional and not entity.array: # not array and optional
        out_str = f'{jtype.classname}(optional=True)'
    
    elif entity.optional and entity.array: # array and optional
        out_str = f'Array({jtype.classname}(), optional=True)'
    
    return out_str

    # if len(types) > 1:
    #     dtype = ', '.join([x.classname for x in types])
    #     dtype = "UnionType(" + dtype + ")"
    # else:
    #     dtype = types[0].classname

    

