



from dataclasses import dataclass, field
from enum import Enum, auto


class ImportType(Enum):
    DATATYPE = auto()
    JANIS_CLASS = auto()
    TOOL_DEF = auto()
    STEP_DEF = auto()

itype_map = {
    'datatype': ImportType.DATATYPE,
    'janiscls': ImportType.JANIS_CLASS,
    'tooldef': ImportType.TOOL_DEF,
    'stepdef': ImportType.STEP_DEF,
}

@dataclass
class Import:
    path: str
    entity: str
    str_itype: str = field(init=False)
    
    def __post_init__(self):
        self.itype: ImportType = itype_map[self.str_itype]



