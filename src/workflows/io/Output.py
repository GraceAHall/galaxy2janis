


from dataclasses import dataclass, field
from datatypes.JanisDatatype import JanisDatatype
from datatypes.formatting import format_janis_str


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
    source_step: str
    source_tag: str
    gx_datatypes: list[str]
    janis_datatypes: list[JanisDatatype] = field(default_factory=list)

    def get_janis_datatype_str(self) -> str:
        return format_janis_str(
            datatypes=self.janis_datatypes,
            is_optional=False,
            is_array=False  # TODO allow array outputs
        )





