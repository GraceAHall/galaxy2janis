



from abc import ABC, abstractmethod
from typing import Any


class Param(ABC):
    name: str
    datatypes: list[str] = []

    @abstractmethod
    def get_default(self) -> Any:
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



