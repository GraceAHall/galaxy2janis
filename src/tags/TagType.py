




from enum import Enum, auto


class TagType(Enum):
    TOOL_NAME       = auto()
    TOOL_COMPONENT  = auto()
    WORKFLOW_NAME   = auto()
    WORKFLOW_STEP   = auto()
    WORKFLOW_INPUT  = auto()
    WORKFLOW_OUTPUT = auto()