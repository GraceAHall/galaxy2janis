

from datetime import datetime
from typing import Optional
from janis.imports.Import import Import

DATE_FORMAT = "%Y-%m-%d"


# GENERAL ----------------------------------

def import_snippet(imp: Import) -> str:
    return f'from {imp.path} import {imp.entity}\n'

def path_append_snippet() -> str:
    return """
import sys
sys.path.append('/home/grace/work/pp/gxtool2janis')
"""

def gxtool2janis_note_snippet(
    workflow_name: str,
    workflow_version: str,
) -> str:
    return f"""
# NOTE
# This is an automated translation of the '{workflow_name}' version '{workflow_version}' workflow. 
# Translation was performed by the gxtool2janis program (in-development)
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
    title_line = f'# STEP{step_count}: {tool_tag.upper()}\n'
    border = f'# {"=" * (len(title_line) - 2)}\n'
    return border + title_line + border

def step_foreward_snippet() -> str:
    return"""
\"\"\"

FOREWORD ----------

RUNTIME VALUES
    ...

PRE TASK, TOOL STEP, POST TASK
    ...

\"\"\"
    """

def step_runtime_input_snippet(input_tag: str, dtype_string: str) -> str:
    return f'w.input("{input_tag}", {dtype_string})\n'

def step_unlinked_value_snippet(text_value: str) -> str:
    return f'#UNKNOWN={text_value}\n'

def step_linked_value_snippet(
    line_len: int,
    tag_and_value: str,
    label: Optional[str],
    argument: str,
    datatype: str
) -> str:
    left = tag_and_value
    right = '# '
    if label:
        right += f'{label.upper()} '
    right += f'({argument}) '
    right += f'[{datatype.upper()}]'
    return f'{left:<{line_len+2}}{right}'

"""

def workflow_step_snippet(
    tag: str,
    tool: str, # represents a tool. need to import this and the import has to be a written janis tool definition
    linked_values: list[Tuple[str, str]],
    unlinked_values: list[Tuple[str, str]],
    scatter: Optional[str]=None,
    doc: Optional[str]=None
) -> str:
    out_str: str = ''
    out_str += 'w.step(\n'
    out_str += f'\t"{tag}",\n'
    out_str += f'\tscatter="{scatter}",\n' if scatter else ''
    out_str += f'\t{tool}(\n'
    for tag, value in unlinked_values:
        out_str += f'\t\t{tag}={value},\n'
    for tag, value in linked_values:
        out_str += f'\t\t{tag}={value},\n'
    out_str += '\t)'
    out_str += f',\n\tdoc="{doc}"' if doc else ''
    out_str += '\n)\n'
    return out_str

def format_step_workflow_inputs(workflow: Workflow, step: WorkflowStep) -> str:
    # for step workflow inputs - get (tag, inp) 
    step_wflow_inputs = [inp for inp in workflow.inputs if inp.step_id == step.metadata.step_id]
    step_wflow_inputs = [(workflow.tag_manager.get(inp.get_uuid()), inp) for inp in step_wflow_inputs]
    step_wflow_inputs.sort(key=lambda x: x[0])
    out_str: str = ''
    for tag, inp in step_wflow_inputs:
        out_str += snippets.workflow_input_snippet(
            tag=tag,
            datatype=inp.get_janis_datatype_str(),
            doc=format_docstring(inp)
        )
    return out_str

def format_step_body(workflow: Workflow, step: WorkflowStep) -> str:
    step_tag = workflow.tag_manager.get(step.get_uuid())
    tool_tag = step.tool.tag_manager.get(step.tool.get_uuid()) #type: ignore
    linked_values = step.get_tool_tags_values()
    linked_values = format_linked_tool_values(linked_values, workflow)
    unlinked_values = step.get_unlinked_values()
    unlinked_values = format_unlinked_tool_values(unlinked_values, workflow)
    return snippets.workflow_step_snippet(
        tag=step_tag,
        tool=tool_tag,
        linked_values=linked_values,
        unlinked_values=unlinked_values, 
        doc=format_docstring(step)
    )

def format_linked_tool_values(tags_inputs: list[Tuple[str, InputValue]], workflow: Workflow, ignore_defaults: bool=True) -> list[Tuple[str, str]]:
    # provides the final list of tool input tags & values. 
    # logic for whether to write inputs if they are default, should wrap with quotes etc
    out: list[Tuple[str, str]] = []
    for comp_tag, input_value in tags_inputs:
        if input_value.is_default_value and ignore_defaults:
            pass
        else:
            formatted_value = format_value(input_value, workflow)
            out.append((comp_tag, formatted_value))
    return out

"""