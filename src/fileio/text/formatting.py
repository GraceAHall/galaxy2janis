

from typing import Any, Optional, Tuple

from gx.command.components import CommandComponent
from gx.command.components import InputComponent
from gx.command.components import Option

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
    jtype = datatypes.get(component)
    if jtype.classname == 'Int' or jtype.classname == 'Float':
        return False
    elif default is None:
        return False
    return True

def datatype_permits_default(jtype: datatypes.JanisDatatype) -> bool:
    # check this component's datatypes permit a default value
    types_with_allowed_default = ['String', 'Float', 'Int', 'Boolean', 'Double']
    if jtype.classname in types_with_allowed_default:
        return True
    return False

def format_imports(imports: list[Tuple[str, str]]) -> str:
    out_str: str = ''
    for x in imports:
        out_str += f'from {x[0]} import {x[1]}\n'
    return out_str