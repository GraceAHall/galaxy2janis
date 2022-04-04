


from dataclasses import dataclass, field
from typing import Optional
from datatypes.JanisDatatype import JanisDatatype
from datatypes.formatting import format_janis_str
from uuid import uuid4

"""
JANIS
Workflow.output(
    identifier: str,
    datatype: DataType = None,
    source: Node = None,
    output_folder: List[Union[String, Node]] = None,
    output_name: Union[String, Node] = None
)
eg 
w.output("out", source=w.sortsam.out)
"""




@dataclass
class WorkflowOutput:
    source_tag: str
    source_output: str
    janis_datatypes: list[JanisDatatype] = field(default_factory=list)

    def __post_init__(self):
        self.uuid: str = str(uuid4())

    def get_uuid(self) -> str:
        return self.uuid
    
    def get_docstring(self) -> Optional[str]:
        return 'None yet!'
        raise NotImplementedError()

    def get_janis_datatype_str(self) -> str:
        return format_janis_str(
            datatypes=self.janis_datatypes,
            is_optional=False,
            is_array=False  # TODO allow array outputs
        )





