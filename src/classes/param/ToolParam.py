



from abc import ABC, abstractmethod
#from dataclasses import dataclass
#from enum import Enum, auto
from typing import Optional, Any, Union


# class ParamType(Enum):
#     TEXT = auto()
#     INTEGER = auto()
#     FLOAT = auto()
#     BOOLEAN = auto()
#     DATA = auto()
#     FLOAT = auto()


class ToolParam(ABC):
    def __init__(self, name: str):
        self.name = name
        self.argument: Optional[str] = None
        self.optional: bool = False
        self.label: Optional[str] = None
        self.helptext: Optional[str] = None

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



