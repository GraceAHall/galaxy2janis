
from typing import Any, Optional
from xmltool.param.Param import Param


class OutputParam(Param):
    def __init__(self, name: str):
        self.name: str = name
        self.label: str = ''
        self.datatypes: list[str] = []
        self.wildcard_pattern: Optional[str] = None

    def get_default(self) -> Any:
        return None

    def get_docstring(self) -> str:
        if self.label:
            return str(self.label)
        return ''
    
    def is_optional(self) -> bool:
        return False
    
    def is_array(self) -> bool:
        return False


class DataOutputParam(OutputParam):
    def __init__(self, name: str, wildcard_pattern: Optional[str]=None):
        super().__init__(name)
        self.wildcard_pattern = wildcard_pattern

    def is_array(self) -> bool:
        if self.wildcard_pattern and '*' in self.wildcard_pattern:
            return True
        return False


class CollectionOutputParam(OutputParam):
    def __init__(self, name: str, wildcard_pattern: Optional[str]=None):
        super().__init__(name)
        self.wildcard_pattern = wildcard_pattern
        self.collection_type: str = 'list'

    def is_array(self) -> bool:
        return True

