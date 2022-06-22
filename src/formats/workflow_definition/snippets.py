

from datetime import datetime
from typing import Optional
from formats.workflow_definition.ToolInputLine import ToolInputLine
from fileio.imports.Import import Import
from entities.workflow.step.tool_values import InputValue

DATE_FORMAT = "%Y-%m-%d"


# GENERAL ----------------------------------

def import_snippet(imp: Import) -> str:
    return f'from {imp.path} import {imp.entity}\n'

def gxtool2janis_note_snippet(
    workflow_name: str,
    workflow_version: str,
) -> str:
    return f"""# NOTE
# This is an automated translation of the '{workflow_name}' version '{workflow_version}' workflow. 
# Translation was performed by the gxtool2janis program (in-development)
"""

def path_append_snippet() -> str:
    return """import sys
sys.path.append('/home/grace/work/pp/gxtool2janis')
"""


# WORKFLOW ---------------------------------

def workflow_metadata_snippet(
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

def workflow_output_snippet(
    tag: str,
    datatype: str,
    step_tag: str,
    toolout_tag: str, 
    output_folder: Optional[str]=None,
    output_name: Optional[str]=None,
    extension: Optional[str]=None,
    doc: Optional[str]=None
) -> str:
    out_str: str = ''
    out_str += 'w.output(\n'
    out_str += f'\t"{tag}",\n'
    out_str += f'\t{datatype},\n'
    out_str += f'\tsource=(w.{step_tag}, "{toolout_tag}")'
    out_str += f',\n\toutput_folder="{output_folder}"' if output_folder else ''
    out_str += f',\n\toutput_name="{output_name}"' if output_name else ''
    out_str += f',\n\textension="{extension}"' if extension else ''
    out_str += f',\n\tdoc="{doc}"' if doc else ''
    out_str += '\n)\n'
    return out_str

def workflow_translate_snippet(toolname: str) -> str:
    return f"""
if __name__ == "__main__":
    w.translate("cwl", **args)
    w.translate("wdl", **args)
"""

# STEP -------------------------------------

def step_title_snippet(step_count: int, tool_tag: str) -> str: 
    TITLE = f'# STEP{step_count}: {tool_tag.upper()}'
    BORDER = f'# {"=" * (len(TITLE) - 2)}'

    return f"""{BORDER}
{TITLE}
{BORDER}
"""

def step_foreward_snippet() -> str:
    return"""\"\"\"
FOREWORD ----------
Please see [WEBLINK] for information on RUNTIME VALUES
Please see [WEBLINK] for information on the PRE TASK, TOOL STEP, POST TASK structure
\"\"\"
"""

def pre_task_snippet() -> str:
    return '# __PRE_TASK__\n'

def post_task_snippet() -> str:
    return '# __POST_TASK__\n'

def step_runtime_input_snippet(input_tag: str, dtype_string: str) -> str:
    return f'w.input("{input_tag}", {dtype_string})\n'

def step_unlinked_value_snippet(text_value: str, input_value: InputValue) -> str:
    return f'\t\t#UNKNOWN={text_value},  # TODO \n'

def step_input_value_snippet(
    line_len: int,
    line: ToolInputLine
) -> str:
    left = line.tag_and_value
    right = '#'
    if line.special_label:
        right += f' {line.special_label}'
    if line.argument:
        right += f' {line.argument}'
    right += f' [{line.datatype}]'
    if line.default:
        right += f' [GALAXY DEFAULT]'
    justified = f'\t\t{left:<{line_len+2}}{right}\n'
    return justified
