
from typing import Optional

from tool.param.Param import Param


class OutputParam(Param):
    def __init__(self, name: str):
        self.name: str = name
        self.label: str = ''
        self.datatypes: list[str] = []
        self.files_wildcard: Optional[str] = ''
        #self.format_source: Optional[str] = '' TODO later
        #self.metadata_source: Optional[str] = '' TODO later

    def get_default(self) -> Optional[str]:
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
    def __init__(self, name: str):
        super().__init__(name)

    def is_array(self) -> bool:
        if self.files_wildcard and '*' in self.files_wildcard:
            return True
        return False


class CollectionOutputParam(OutputParam):
    def __init__(self, name: str):
        super().__init__(name)
        self.collection_type: str = 'list'

    def is_array(self) -> bool:
        return True

