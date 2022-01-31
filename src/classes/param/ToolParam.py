



from abc import ABC, abstractmethod
#from dataclasses import dataclass
#from enum import Enum, auto
from typing import Optional


# class ParamType(Enum):
#     TEXT = auto()
#     INTEGER = auto()
#     FLOAT = auto()
#     BOOLEAN = auto()
#     DATA = auto()
#     FLOAT = auto()



class ToolParam(ABC):
    def __init__(self, name: str, heirarchy: list[str]):
        self.name: str = name
        self.heirarchy: list[str] = []
        self.optional: bool = False
        self.argument: Optional[str] = None  ## i dont know if this is needed
        self.label: Optional[str] = None
        self.helptext: Optional[str] = None

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



