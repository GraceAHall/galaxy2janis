

from typing import Any, Optional
from datetime import datetime
DATE_FORMAT = "%Y-%m-%d"


def path_append_snippet() -> str:
    return """
import sys
sys.path.append('/home/grace/work/pp/gxtool2janis')
"""


def metadata_snippet(
    tool_name: str,
    tool_version: str,
    url: Optional[str]=None,
    wrapper_owner: Optional[str]=None,
    wrapper_creator: Optional[str]=None,
    doi: Optional[str]=None,
    citation:Optional[str]=None
) -> str:
    doi = f'"{doi}"' if doi else None
    url = url if url else ''
    contrib_str = 'gxtool2janis'
    if wrapper_owner:
        contrib_str += f', Galaxy Toolshed Username: {wrapper_owner}'
    if wrapper_creator:
        contrib_str += f', Galaxy Wrapper Creator: {wrapper_creator}'
    return f"""
metadata = ToolMetadata(
    short_documentation="gxtool2janis translation of '{tool_name}' version '{tool_version}' from Galaxy XML wrapper {url}",
    contributors="{contrib_str}",
    dateCreated="{datetime.today().strftime(DATE_FORMAT)}",
    dateUpdated="{datetime.today().strftime(DATE_FORMAT)}",
    version=0,
    doi={doi},
    citation="{citation}"
)

"""

def tool_input_snippet(
    tag: str,
    datatype: str,
    prefix: Optional[str]=None,
    kv_space: Optional[bool]=None,
    position: Optional[int]=None,
    default: Optional[Any]=None,
    doc: Optional[str]=None
) -> str:
    out_str: str = ''
    out_str += '\n\tToolInput(\n'
    out_str += f"\t\t'{tag}',\n"
    out_str += f"\t\t{datatype},\n"
    out_str += f"\t\tprefix='{prefix}',\n" if prefix else ''
    out_str += f"\t\tseparate_value_from_prefix={kv_space},\n" if kv_space == False else ''
    out_str += f"\t\tposition={position},\n" if position else ''
    out_str += f"\t\tdefault={default},\n" if default else ''
    out_str += f'\t\tdoc="{doc}",\n' if doc else ''
    out_str += '\t)'
    return out_str
    

def tool_output_snippet(
    tag: str,
    datatype: str,
    selector: Optional[str],
    doc: Optional[str]=None
) -> str:
    out_str: str = ''
    out_str += '\n\tToolOutput(\n'
    out_str += f"\t\t'{tag}',\n"
    out_str += f"\t\t{datatype},\n"
    if selector:
        out_str += f"\t\tselector={selector},\n" 
    out_str += f'\t\tdoc="{doc}",\n' if doc else ''
    out_str += '\t)'
    return out_str


def command_tool_builder_snippet(
    toolname: str, 
    base_command: list[str], 
    container: str, 
    version: str, 
    help: str) -> str:
    return f"""
{toolname} = CommandToolBuilder(
    tool="{toolname}",
    base_command={base_command},
    metadata=metadata,
    inputs=inputs,
    outputs=outputs,
    container="{container}",
    version="{version}",
    doc=\"\"\"{str(help)}\"\"\"
)\n"""
# missing from command_tool_builder_snippet()
#out_str += f'\tfriendly_name="{friendly_name}",\n'
#out_str += f'\targuments="{arguments}",\n'
#out_str += f'\tenv_vars="{env_vars}",\n'
#out_str += f'\ttool_module="{tool_module}",\n'
#out_str += f'\ttool_provider="{citation}",\n'
#out_str += f'\tcpus="{cpus}",\n'
#out_str += f'\tmemory="{memory}",\n'
#out_str += f'\ttime="{time}",\n'
#out_str += f'\tdisk="{disk}",\n'
#out_str += f'\tdirectories_to_create="{directories_to_create}",\n'
#out_str += f'\tfiles_to_create="{files_to_create}",\n'


def translate_snippet(toolname: str) -> str:
    return f"""
if __name__ == "__main__":
    {toolname}().translate(
        "wdl", to_console=True
    )\n
"""