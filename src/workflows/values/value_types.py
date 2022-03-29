




from typing import Any

from command.components.CommandComponent import CommandComponent
from workflows.values.InputValue import InputValueType

import utils.general_utils as utils


def select_input_value_type(component: CommandComponent, value: Any) -> InputValueType:
    """
    only StaticValueLinkingStrategy and DefaultValueLinkingStrategy 
    call this function. don't need to worry about CONNECTION and RUNTIME_VALUE
    STRING          = auto()
    NUMERIC         = auto()
    BOOLEAN         = auto()
    NONE            = auto()
    """
    if is_bool(component, value):
        return InputValueType.BOOLEAN
    elif is_numeric(component, value):
        return InputValueType.NUMERIC
    elif is_none(component, value):
        return InputValueType.NONE
    else:
        return InputValueType.STRING

def is_bool(component: CommandComponent, value: Any) -> bool:
    if isinstance(value, bool):
        return True
    return False

def is_none(component: CommandComponent, value: Any) -> bool:
    if value is None:
        return True
    return False

def is_numeric(component: CommandComponent, value: Any) -> bool:
    if has_numeric_datatype(component):
        if utils.is_int(str(value)) or utils.is_float(str(value)):
            return True
    return False

def has_numeric_datatype(component: CommandComponent) -> bool:
    datatypes = set([x.classname for x in component.janis_datatypes])
    exclusions = ['Int', 'Float']
    if any([x in datatypes for x in exclusions]): 
        return True
    return False
    