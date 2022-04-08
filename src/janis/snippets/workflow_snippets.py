

from typing import Optional, Tuple
from janis_core import WorkflowBuilder
from datetime import datetime

from workflows.step.values.InputValue import InputValue


DATE_FORMAT = "%Y-%m-%d"

w = WorkflowBuilder("alignmentWorkflow")

def gxtool2janis_note_snippet(
    workflow_name: str,
    workflow_version: str,
) -> str:
    return f"""
# NOTE
# This is an automated translation of the '{workflow_name}' version '{workflow_version}' workflow. 
# Translation was performed by the gxtool2janis program (in-development)

"""

def path_append_snippet() -> str:
    return """import sys
sys.path.append('/home/grace/work/pp/gxtool2janis')

"""

def metadata_snippet(
    tags: list[str],
    annotation: str,
    version: str,
    doi: Optional[str]=None,
    citation:Optional[str]=None
) -> str:
    doi = f'"{doi}"' if doi else None
    citation = f'"{citation}"' if citation else None
    contributors = ['gxtool2janis']
    return f"""metadata = WorkflowMetadata(
    short_documentation="{annotation}",
    contributors={contributors},
    keywords={tags},
    dateCreated="{datetime.today().strftime(DATE_FORMAT)}",
    dateUpdated="{datetime.today().strftime(DATE_FORMAT)}",
    version={version},
    doi={doi},
    citation={citation}
)

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
    out_str += f'\t"{tag}"'
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
    out_str += f'w.input("{tag}", {datatype})\n'
    #out_str += f'\t"{tag}",\n'
    #out_str += f'\t{datatype}'
    #out_str += f',\n\tdefault={default}' if default else ''
    #out_str += f',\n\tvalue={value}' if value else ''
    #out_str += f',\n\tdoc="{doc}"' if doc else ''
    #out_str += '\n)\n'
    return out_str


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
    tool_input_values: list[Tuple[str, str]],
    unlinked_values: list[str],
    scatter: Optional[str]=None,
    doc: Optional[str]=None
) -> str:
    out_str: str = ''
    out_str += 'w.step(\n'
    out_str += f'\t"{tag}",\n'
    out_str += f'\tscatter="{scatter}",\n' if scatter else ''
    out_str += f'\t{tool}(\n'
    for value in unlinked_values:
        out_str += f'\t\t#UNKNOWN={value},\n'
    for tag, value in tool_input_values:
        out_str += f'\t\t{tag}={value},\n'
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
    step_tag: str,
    step_output: str, 
    output_folder: Optional[str]=None,
    output_name: Optional[str]=None,
    extension: Optional[str]=None,
    doc: Optional[str]=None
) -> str:
    out_str: str = ''
    out_str += 'w.output(\n'
    out_str += f'\t"{tag}",\n'
    out_str += f'\t{datatype},\n'
    out_str += f'\tsource=(w.{step_tag}, "{step_output}")'
    out_str += f',\n\toutput_folder="{output_folder}"' if output_folder else ''
    out_str += f',\n\toutput_name="{output_name}"' if output_name else ''
    out_str += f',\n\textension="{extension}"' if extension else ''
    out_str += f',\n\tdoc="{doc}"' if doc else ''
    out_str += '\n)\n'
    return out_str


def translate_snippet(toolname: str) -> str:
    return f"""

if __name__ == "__main__":
    w.translate("cwl", **args)
    w.translate("wdl", **args)

"""



"""
SHAME CORNER


    # if 'positional' in tool_input_values:
    #     out_str += f'\t\t# Positionals\n'
    #     for name, value in tool_input_values['positional']:
    #         out_str += f'\t\t{name}={value},\n'
    # if 'flag' in tool_input_values:
    #     out_str += f'\t\t# Flags (boolean options)\n'
    #     for name, value in tool_input_values['flag']:
    #         out_str += f'\t\t{name}={value},\n'
    # if 'option' in tool_input_values:
    #     out_str += f'\t\t# Options\n'
    #     for name, value in tool_input_values['option']:
    #         out_str += f'\t\t{name}={value},\n'
"""