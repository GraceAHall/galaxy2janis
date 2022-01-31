

from dataclasses import dataclass
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


class GenericInputParam(Param):
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


class TextParam(GenericInputParam):
    value: Optional[str] = None

    def get_default(self) -> Optional[str]:
        if self.value:
            return self.value
        return None
    

class IntegerParam(GenericInputParam):
    value: Optional[str] = None
    min: Optional[str] = None
    max: Optional[str] = None

    def get_default(self) -> Optional[str]:
        if self.value:
            return self.value
        elif self.min:
            return self.min
        elif self.max:
            return self.max
        return None


# YES I KNOW THIS IS ESSENTIALLY DUPLICATED FROM INTEGERParam SUE ME
class FloatParam(GenericInputParam):
    value: Optional[str] = None
    min: Optional[str] = None
    max: Optional[str] = None

    def get_default(self) -> Optional[str]:
        if self.value:
            return self.value
        elif self.min:
            return self.min
        elif self.max:
            return self.max
        return None


class BoolParam(GenericInputParam):
    def __init__(self, name: str, heirarchy: list[str]):
        super().__init__(name, heirarchy)
        self.checked: bool = False
        self.truevalue: str = ''
        self.falsevalue: str = ''

    def get_default(self) -> str:
        if self.checked:
            return self.truevalue
        return self.falsevalue

    def get_docstring(self) -> str:
        docstring = generic_get_docstring(self)
        bool_values = [self.truevalue, self.falsevalue]
        bool_values = [v for v in bool_values if v != '']
        bool_str = ', '.join(bool_values)
        return f'{docstring}. possible values: {bool_str}'
    
    def is_optional(self) -> bool:
        return True


@dataclass
class SelectOption:
    value: str
    selected: bool
    ui_text: str

class SelectParam(GenericInputParam):
    def __init__(self, name: str, heirarchy: list[str], options: list[SelectOption], multiple: bool):
        super().__init__(name, heirarchy)
        self.options = options
        self.multiple = multiple

    def get_default(self) -> Optional[str]:
        for option in self.options:
            if option.selected:
                return option.value
        return None        

    def get_docstring(self) -> str:
        docstring = generic_get_docstring(self)
        option_values = [v.value for v in self.options]
        option_str = ', '.join(option_values[:5])
        return f'{docstring}. possible values: {option_str}'
    
    def is_optional(self) -> bool:
        if self.multiple or self.optional:
            return True
        return False
    
    def is_array(self) -> bool:
        if self.multiple:
            return True
        return False


class DataParam(GenericInputParam):
    def __init__(self, name: str, heirarchy: list[str], format: str, multiple: bool):
        super().__init__(name, heirarchy)
        self.format = format
        self.multiple = multiple
    
    def is_array(self) -> bool:
        return self.multiple


class DataCollectionParam(GenericInputParam):
    def __init__(self, name: str, heirarchy: list[str], format: str):
        super().__init__(name, heirarchy)
        self.format = format
    
    def is_array(self) -> bool:
        return True

