



from abc import ABC, abstractmethod
from typing import Optional


class Param(ABC):
    name: str

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



