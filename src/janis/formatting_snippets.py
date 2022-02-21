




from typing import Optional


def tool_input_snippet(
    tag: str,
    datatype: str,
    prefix: Optional[str]=None,
    separator: Optional[str]=None,
    separate_value_from_prefix: Optional[bool]=None,
    position: Optional[int]=None,
    default: Optional[str]=None,
    doc: Optional[str]=None
) -> str:
    return f"""
    ToolInput(
        "{tag}",
        {datatype},
        prefix="{prefix}",
        separator="{separator}",
        separate_value_from_prefix={separate_value_from_prefix},
        position={position},
        default={default},
        doc="{doc}"
    )"""


def tool_output_snippet(
    tag: str,
    datatype: str,
    selector_type: str,
    selector_contents: str,
    doc: Optional[str]=None
) -> str:
    return f"""
    ToolOutput(
        "{tag}",
        {datatype},
        selector={selector_type}("{selector_contents}")
        doc="{doc}"
    )"""


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
    inputs=fastp_inputs,
    outputs=fastp_outputs,
    container="{container}",
    version="{version}",
    doc={help}
)"""

# missing from command_tool_builder_snippet()
#out_str += f'\tfriendly_name="{friendly_name}",\n'
#out_str += f'\targuments="{arguments}",\n'
#out_str += f'\tenv_vars="{env_vars}",\n'
#out_str += f'\ttool_module="{tool_module}",\n'
#out_str += f'\ttool_provider="{citation}",\n'
#out_str += f'\tmetadata="{metadata}",\n'
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
    )
"""