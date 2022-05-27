



from abc import ABC, abstractmethod
from typing import Any


class Param(ABC):
    name: str
    datatypes: list[str] = []

    @property
    @abstractmethod
    def default(self) -> Any:
        ...

    @property
    @abstractmethod
    def docstring(self) -> str:
        ...
    
    @property
    @abstractmethod
    def optional(self) -> bool:
        ...
    
    @property
    @abstractmethod
    def array(self) -> bool:
        ...



