








from typing import Optional, Protocol


class Param(Protocol):
    name: str
    label: str = ''
    helptext: str = ''
    optional: bool = False
    argument: Optional[str] = None
    
    def get_default(self) -> Optional[str]:
        ...

    def get_docstring(self) -> str:
        ...
    
    def is_optional(self) -> bool:
        ...
    
    def is_array(self) -> bool:
        ...


class GenericInputParam:
    def __init__(self, name: str):
        self.name: str = name
        self.label: str = ''
        self.helptext: str = ''
        self.optional: bool = False
        self.argument: Optional[str] = None  ## i dont know if this is needed
      
    def get_default(self) -> Optional[str]:
        return None

    def get_docstring(self) -> str:
        return ''
    
    def is_optional(self) -> bool:
        return self.optional
    
    def is_array(self) -> bool:
        return False


class TextParam(GenericInputParam):
    def __init__(self, name: str):
        super().__init__(name)
        self.value: Optional[str] = None

    def get_default(self) -> Optional[str]:
        if self.value:
            return self.value
        return None


class IntegerParam(GenericInputParam):
    def __init__(self, name: str):
        super().__init__(name)
        self.value: Optional[str] = None
        self.min: Optional[str] = None
        self.max: Optional[str] = None

    def get_default(self) -> Optional[str]:
        if self.value:
            return self.value
        elif self.min:
            return self.min
        elif self.max:
            return self.max
        return None


def myfunc(param: Param) -> Param:
    return param


myparam = TextParam('param1')
myfunc(myparam)