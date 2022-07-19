

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

def get_str(entity: FormattableEntity, fmt: str='definition') -> str:
    jtype = get(entity=entity)
    if fmt == 'definition':
        return fmt_typestr_definition(entity, jtype)
    elif fmt == 'value':
        return fmt_typestr_value(entity, jtype)
    else:
        raise RuntimeError()

def fmt_typestr_definition(entity: FormattableEntity, jtype: JanisDatatype) -> str:
    # not array not optional
    if not entity.optional and not entity.array: 
        out_str = f'{jtype.classname}'
    
    # array and not optional
    elif not entity.optional and entity.array: 
        out_str = f'Array({jtype.classname})'
    
    # not array and optional
    elif entity.optional and not entity.array: 
        out_str = f'{jtype.classname}(optional=True)'
    
    # array and optional
    elif entity.optional and entity.array: 
        out_str = f'Array({jtype.classname}(), optional=True)'
    return out_str

    # if len(types) > 1:
    #     dtype = ', '.join([x.classname for x in types])
    #     dtype = "UnionType(" + dtype + ")"
    # else:
    #     dtype = types[0].classname

def fmt_typestr_value(entity: FormattableEntity, jtype: JanisDatatype) -> str:
    # not array not optional
    if not entity.optional and not entity.array: 
        out_str = f'{jtype.classname}'
    
    # array and not optional
    elif not entity.optional and entity.array: 
        out_str = f'{jtype.classname} ARRAY'
    
    # not array and optional
    elif entity.optional and not entity.array: 
        out_str = f'{jtype.classname} OPTIONAL'
    
    # array and optional
    elif entity.optional and entity.array: 
        out_str = f'{jtype.classname} ARRAY OPTIONAL'
    return out_str

    # if len(types) > 1:
    #     dtype = ', '.join([x.classname for x in types])
    #     dtype = "UnionType(" + dtype + ")"
    # else:
    #     dtype = types[0].classname

    

