



from abc import ABC, abstractmethod
from typing import Optional


class Param(ABC):
    def __init__(self, name: str):
        self.name: str = name
        self.label: str = ''
        self.helptext: str = ''
        self.optional: bool = False
        self.argument: Optional[str] = None  ## i dont know if this is needed

    @abstractmethod
    def get_var_name(self) -> str:
        ...
    
    @abstractmethod
    def get_default(self) -> Optional[str]:
        ...

    @abstractmethod
    def get_docstring(self) -> str:
        ...
    
    @abstractmethod
    def is_optional(self) -> bool:
        ...
    
    @abstractmethod
    def is_array(self) -> bool:
        ...



