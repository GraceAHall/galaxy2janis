


from dataclasses import dataclass
from enum import Enum, auto


class ImportType(Enum):
    DATATYPE = auto()
    JANIS_CLASS = auto()
    TOOL_DEF = auto()
    STEP_DEF = auto()

@dataclass
class Import:
    path: str
    entity: str
    itype: ImportType

        



