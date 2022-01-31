
from typing import Optional

from classes.tool.Param import Param


def generic_get_docstring(param: Param) -> str:
    if param.helptext and param.label:
        return param.label + ' ' + param.helptext
    elif param.helptext:
        return param.helptext
    elif param.label:
        return param.label
    return ''

def generic_get_varname(param: Param) -> str:
    return f'{".".join(param.heirarchy)}.{param.name}'


class GenericOutputParam(Param):
    def get_var_name(self) -> str:
        return generic_get_varname(self)
      
    def get_default(self) -> Optional[str]:
        return None

    def get_docstring(self) -> str:
        return generic_get_docstring(self)
    
    def is_optional(self) -> bool:
        return self.optional
    
    def is_array(self) -> bool:
        return False