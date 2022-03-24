

from typing import Any, Optional, Tuple
from janis_core import WorkflowBuilder
w = WorkflowBuilder("alignmentWorkflow")


def path_append_snippet() -> str:
    return """
import sys
sys.path.append('homegraceworkppgxtool2janis')
"""


# WORKFLOWBUILDER
"""
w = WorkflowBuilder("alignmentWorkflow")
"""
def workflow_builder_snippet(
    tag: str,
    friendly_name: Optional[str]=None,
    version: Optional[str]=None,
    doc: Optional[str]=None,
) -> str:
    out_str: str = ''
    out_str += 'w = WorkflowBuilder(\n'
    out_str += f'\t"{tag}",\n'
    out_str += f',\n\tfriendly_name="{friendly_name}"' if friendly_name else ''
    out_str += f',\n\tversion="{version}"' if version else ''
    out_str += f',\n\tdoc="{doc}"' if doc else ''
    out_str += '\n)\n'
    return out_str


# INPUTS
"""
w.input("sample_name", String)
w.input("read_group", String)
w.input("fastq", FastqGzPairedEnd)
"""
def workflow_input_snippet(
    tag: str,
    datatype: str,
    default: Optional[str]=None,
    value: Optional[str]=None,
    doc: Optional[str]=None
) -> str:
    out_str: str = ''
    out_str += 'w.input(\n'
    out_str += f'\t"{tag}",\n'
    out_str += f'\t{datatype}'
    out_str += f',\n\tdefault={default}' if default else ''
    out_str += f',\n\tvalue={value}' if value else ''
    out_str += f',\n\tdoc="{doc}"' if doc else ''
    out_str += '\n)'
    return out_str



"""
working dir 
tools
    - parsed fastqc
    - parsed ...
simple_workflow.py
steps
    - step1_fastqc.py -> toolsfastqc
        step1 preprocess
        step1 main
        step1 postprocess
    - step1_fastqc.py
    - step1_fastqc.py

"""



# STEPS
"""
w.step(
    "bwamem", 
    BwaMemLatest( 
        reads=w.fastq, 
        readGroupHeaderLine=w.read_group, 
        reference=w.reference
    )
)
"""
def workflow_step_snippet(
    tag: str,
    tool: str, # represents a tool. need to import this and the import has to be a written janis tool definition
    tool_input_values: list[Tuple[str, Any]],
    scatter: Optional[str]=None,
    doc: Optional[str]=None
) -> str:
    out_str: str = ''
    out_str += 'w.step(\n'
    out_str += f'\t"{tag}",\n'
    out_str += f'\tscatter="{scatter}",\n' if scatter else ''
    out_str += f'\t{tool}(\n'
    for name, value in tool_input_values:
        out_str += f'\t\t{name}={value},\n'
    out_str += '\t)'
    out_str += f',\n\tdoc="{doc}"' if doc else ''
    out_str += '\n)\n'
    return out_str


# OUTPUTS
"""
w.output("out", source=w.sortsam.out)

identifier: str,
datatype: Optional[ParseableType] = None,
source: Union[
    List[Union[Selector, ConnectionSource]], Union[Selector, ConnectionSource]
] = None,
output_folder: Union[str, Selector, List[Union[str, Selector]]] = None,
output_name: Union[bool, str, Selector, ConnectionSource] = True,
extension: Optional[str] = None,
doc: Union[str, OutputDocumentation] = None,
"""
def workflow_output_snippet(
    tag: str,
    datatype: str,
    source: str, 
    # source is either a string which refers to an output of a step, or a Selector. 
    # No idea why this would be a Selector though? ask richard
    output_folder: Optional[str]=None,
    output_name: Optional[str]=None,
    extension: Optional[str]=None,
    doc: Optional[str]=None
) -> str:
    out_str: str = ''
    out_str += 'w.output(\n'
    out_str += f'\t"{tag}",\n'
    out_str += f'\t{datatype},\n'
    out_str += f'\tsource={source}'
    out_str += f',\n\toutput_folder="{output_folder}"' if output_folder else ''
    out_str += f',\n\toutput_name="{output_name}"' if output_name else ''
    out_str += f',\n\textension="{extension}"' if extension else ''
    out_str += f',\n\tdoc="{doc}"' if doc else ''
    out_str += '\n)\n'
    return out_str

