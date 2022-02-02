
from typing import Optional

from tool.param.Param import Param


class OutputParam(Param):
    def __init__(self, name: str):
        self.name: str = name
        self.label: str = ''
        self.format: list[str] = []

    def get_default(self) -> Optional[str]:
        return None

    def get_docstring(self) -> str:
        if self.label:
            label = str(self.label)
            return label.rsplit('}', 1)[-1]
        return ''
    
    def is_optional(self) -> bool:
        return False
    
    def is_array(self) -> bool:
        return False


class DataOutputParam(OutputParam):
    def __init__(self, name: str):
        super().__init__(name)
        self.files_wildcard: Optional[str] = ''


class CollectionOutputParam(OutputParam):
    def __init__(self, name: str):
        super().__init__(name)
        self.files_wildcard: str = ''
        self.collection_type: Optional[str] = ''



