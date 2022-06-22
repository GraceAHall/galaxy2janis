


from dataclasses import dataclass, field
from typing import Optional
from datatypes import JanisDatatype
from datatypes.formatting import format_janis_str
from uuid import uuid4


@dataclass
class WorkflowOutput:
    step_tag: str
    toolout_tag: str
    janis_datatypes: list[JanisDatatype] = field(default_factory=list)

    def __post_init__(self):
        self.uuid: str = str(uuid4())

    @property
    def docstring(self) -> Optional[str]:
        return 'None yet!'

    def get_janis_datatype_str(self) -> str:
        return format_janis_str(
            datatypes=self.janis_datatypes,
            is_optional=False,
            is_array=False  # TODO allow array outputs
        )





