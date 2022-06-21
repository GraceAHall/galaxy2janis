

from typing import Any
from datatypes import JanisDatatype


def datatypes_permit_default(janis_datatypes: list[JanisDatatype]) -> bool:
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


def sanitise_default_value(query_default: Any) -> Any:
    """
    currently disallows $env_vars to be defaults.
    """
    if query_default is not None:
        if query_default.startswith('$'):
            return None
    return query_default