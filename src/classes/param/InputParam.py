



from dataclasses import dataclass
from typing import Optional

from classes.param.ToolParam import ToolParam


def generic_get_docstring(param: ToolParam) -> str:
    if param.helptext and param.label:
        return param.label + ' ' + param.helptext
    elif param.helptext:
        return param.helptext
    elif param.label:
        return param.label
    return ''


class TextToolParam(ToolParam):
    value: Optional[str] = None

    def get_default(self) -> Optional[str]:
        if self.value:
            return self.value
        return None

    def get_docstring(self) -> str:
        return generic_get_docstring(self)
        
    def is_optional(self) -> bool:
        if self.optional:
            return True
        return False
    
    def is_array(self) -> bool:
        return False


class IntegerToolParam(ToolParam):
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

    def get_docstring(self) -> str:
        return generic_get_docstring(self)
    
    def is_optional(self) -> bool:
        if self.optional:
            return True
        return False
    
    def is_array(self) -> bool:
        return False

# YES I KNOW THIS IS ESSENTIALLY DUPLICATED FROM INTEGERTOOLPARAM SUE ME
class FloatToolParam(ToolParam):
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

    def get_docstring(self) -> str:
        return generic_get_docstring(self)
    
    def is_optional(self) -> bool:
        if self.optional:
            return True
        return False
    
    def is_array(self) -> bool:
        return False


class BoolToolParam(ToolParam):
    def __init__(self, name: str):
        super().__init__(name)
        self.checked: bool = True
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
    
    def is_array(self) -> bool:
        return False


@dataclass
class SelectOption:
    value: str
    selected: bool
    ui_text: str

class SelectToolParam(ToolParam):
    def __init__(self, name: str, options: list[SelectOption], multiple: bool):
        super().__init__(name)
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


class DataToolParam(ToolParam):
    def __init__(self, name: str, format: str, multiple: bool):
        super().__init__(name)
        self.format = format
        self.multiple = multiple
      
    def get_default(self) -> Optional[str]:
        return None

    def get_docstring(self) -> str:
        return generic_get_docstring(self)
    
    def is_optional(self) -> bool:
        return self.optional
    
    def is_array(self) -> bool:
        return self.multiple


class DataCollectionToolParam(ToolParam):
    def __init__(self, name: str, format: str):
        super().__init__(name)
        self.format = format
      
    def get_default(self) -> Optional[str]:
        return None

    def get_docstring(self) -> str:
        return generic_get_docstring(self)
    
    def is_optional(self) -> bool:
        return self.optional
    
    def is_array(self) -> bool:
        return True

