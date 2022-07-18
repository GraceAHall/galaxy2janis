
from typing import Any, Optional
from gx.gxtool.param.Param import Param


class OutputParam(Param):
    def __init__(self, name: str):
        self.name: str = name
        self.label: str = ''
        self.formats: list[str] = []
        self.wildcard_pattern: Optional[str] = None

    @property
    def default(self) -> Any:
        return None

    @property
    def docstring(self) -> str:
        if self.label:
            return str(self.label)
        return ''
    
    @property
    def optional(self) -> bool:
        return False
    
    @property
    def array(self) -> bool:
        return False


class DataOutputParam(OutputParam):
    def __init__(self, name: str, wildcard_pattern: Optional[str]=None):
        super().__init__(name)
        self.wildcard_pattern = wildcard_pattern

    @property
    def array(self) -> bool:
        if self.wildcard_pattern and '*' in self.wildcard_pattern:
            return True
        return False


class CollectionOutputParam(OutputParam):
    def __init__(self, name: str, wildcard_pattern: Optional[str]=None):
        super().__init__(name)
        self.wildcard_pattern = wildcard_pattern
        self.collection_type: str = 'list'

    @property
    def array(self) -> bool:
        return True

