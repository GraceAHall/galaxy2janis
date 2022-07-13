

from typing import Any, Optional, Protocol, Tuple

from command import CommandComponent
from command import InputComponent
from command import Option

import datatypes

def format_docstring(component: CommandComponent) -> Optional[str]:
    raw_doc = component.docstring
    if raw_doc:
        return raw_doc.replace('"', "'")
    return None

def get_wrapped_default(component: InputComponent) -> Optional[str]:
    default = component.default_value
    # override env var default values to None 
    # TODO move this. should NOT happen here. 
    # THIS IS SO BAD I CANT EVEN. Should happen when getting default value
    if isinstance(component, Option) and default is not None:
        if '$' in default:
            default = None
    if should_quote(default, component):
        return f'"{default}"'
    return default

def should_quote(default: Any, component: CommandComponent) -> bool:
    jtypes = datatypes.get(component)
    jclasses = [x.classname for x in jtypes]
    if 'Int' in jclasses or 'Float' in jclasses:
        return False
    elif default is None:
        return False
    return True

def datatypes_permit_default(janis_datatypes: list[datatypes.JanisDatatype]) -> bool:
    # check datatypes aren't empty
    if len(janis_datatypes) == 0:
        raise RuntimeError('component.janis_datatypes must be set before a default value can be given')
    # check this component's datatypes permit a default value
    types_with_allowed_default = ['String', 'Float', 'Int', 'Boolean', 'Double']
    datatypes = [x.classname for x in janis_datatypes]
    # at least one of the datatypes must be in the allowlist
    if sum([dtype in types_with_allowed_default for dtype in datatypes]) >= 1:
        return True
    return False


class FormattableEntity(Protocol):
    @property
    def optional(self) -> bool:
        ...

    @property
    def array(self) -> bool:
        ...

def format_datatype_string(entity: FormattableEntity) -> str:
    # if len(types) > 1:
    #     dtype = ', '.join([x.classname for x in types])
    #     dtype = "UnionType(" + dtype + ")"
    # else:
    #     dtype = types[0].classname

    e = entity
    jtypes = datatypes.get(e)
    dtype = jtypes[0].classname  # TODO hack to remove UnionType. 
    
    if not e.optional and not e.array: # not array not optional
        out_str = f'{dtype}'
    
    elif not e.optional and e.array: # array and not optional
        out_str = f'Array({dtype})'
    
    elif e.optional and not e.array: # not array and optional
        out_str = f'{dtype}(optional=True)'
    
    elif e.optional and e.array: # array and optional
        out_str = f'Array({dtype}(), optional=True)'
    
    return out_str

def format_imports(imports: list[Tuple[str, str]]) -> str:
    out_str: str = ''
    for x in imports:
        out_str += f'from {x[0]} import {x[1]}\n'
    return out_str