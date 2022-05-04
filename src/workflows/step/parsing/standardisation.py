

from typing import Any

value_translations = {
        'false': False,
        'False': False,
        'true': True,
        'True': True,
        'null': None,
        'none': None,
        'None': None,
        '': None
    }


def standardise_tool_state_value(value: Any) -> Any:
    value = handle_array(value)
    value = handle_translations(value)
    return value

def handle_array(value: Any) -> Any:
    if isinstance(value, list):
        return None
        # if len(value) == 0:
        #     value = None
        # else:
        #     value = value[0]
    return value

def handle_translations(value: Any) -> Any:
    if value in value_translations:
        return value_translations[value]
    return value
