


from typing import Any, Optional
#from entities.workflow import WorkflowInput

from gx.command.components import CommandComponent
from gx.command.components import InputComponent

import utils.general as utils
import datatypes



def get_comptype(component: CommandComponent) -> str:
    return type(component).__name__.lower() 

def select_input_value_type(component: Optional[InputComponent], value: Any) -> str:
    """
    only StaticValueLinkingStrategy and DefaultValueLinkingStrategy 
    call this function. don't need to worry about CONNECTION and RUNTIME_VALUE
    """
    if is_bool(value):
        return 'boolean'
    elif component and is_numeric(component, value):
        return 'numeric'
    elif is_none(value):
        return 'none'
    elif is_env_var(value) or has_env_var(value):
        return 'env_var'
    else:
        return 'string'

def is_env_var(value: Any) -> bool:
    if str(value).startswith('$'):
        return True
    return False

def has_env_var(value: Any) -> bool:
    if '$' in str(value):
        return True
    return False

def is_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    return False

def is_none(value: Any) -> bool:
    if value is None:
        return True
    return False

def is_numeric(component: CommandComponent, value: Any) -> bool:
    if _has_numeric_datatype(component):
        if utils.is_int(str(value)) or utils.is_float(str(value)):
            return True
    return False

def _has_numeric_datatype(component: CommandComponent) -> bool:
    jtype = datatypes.get(component)
    numeric_classes = ['Int', 'Float']
    if jtype.classname in numeric_classes:
        return True
    return False
    


