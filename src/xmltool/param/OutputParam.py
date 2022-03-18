
from typing import Any, Optional

from xmltool.param.Param import Param
from xmltool.parsing.selectors import Selector


class OutputParam(Param):
    def __init__(self, name: str):
        self.name: str = name
        self.label: str = ''
        self.datatypes: list[str] = []
        self.selector: Optional[Selector] = None

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
    def __init__(self, name: str):
        super().__init__(name)

    def is_array(self) -> bool:
        if self.selector and '*' in self.selector.contents:
            return True
        return False


class CollectionOutputParam(OutputParam):
    def __init__(self, name: str):
        super().__init__(name)
        self.collection_type: str = 'list'

    def is_array(self) -> bool:
        return True

