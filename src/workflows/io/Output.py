






from dataclasses import dataclass


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
    name: str
    step: int
    datatype: str
    output_name: str

