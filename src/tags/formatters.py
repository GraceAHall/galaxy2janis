

from typing import Any
from command.components.inputs.Flag import Flag



def format_capitalisation(tag: str, entity: Any) -> str:
    # allow first letter capital, rest lower
    if len(tag) > 1:
        return tag.lower()
    return tag[0]

def replace_non_alphanumeric(tag: str, entity: Any) -> str:
    """
    to satisfy janis tag requirements
    to avoid janis reserved keywords
    """
    tag = tag.strip('\\/-${}')
    tag = tag.replace('-', '_')
    tag = tag.replace('(', '')
    tag = tag.replace(')', '')
    tag = tag.replace('.', '_')
    tag = tag.replace(' ', '_')
    tag = tag.replace('|', '_')
    tag = tag.replace('/', '_')
    tag = tag.replace('\\', '_')
    tag = tag.replace('"', '')
    tag = tag.replace("'", '')
    tag = tag.replace("@", 'at')
    return tag

prohibited_keys = {
    "identifier",
    "tool",
    "scatter",
    "ignore_missing",
    "output",
    "input",
    "inputs"
}

def handle_prohibited_key(tag: str, entity: Any) -> str:
    if tag in prohibited_keys:
        tag = append_datatype(tag, entity)
    return tag

def handle_short_tag(tag: str, entity: Any) -> str:
    if len(tag) == 1:
        if isinstance(entity, Flag):
            tag = f'{tag}_flag'
        else:
            tag = f"input_{tag}"
            # if hasattr(entity, 'janis_datatypes'):
            #     tag = append_datatype(tag, entity)
    return tag

def append_datatype(tag: str, entity: Any) -> str:
    dtype = entity.janis_datatypes[0].classname.lower()
    if not tag.endswith(dtype): # don't add the dtype if its already been added
        tag = f"{tag}_{dtype}"
    return tag

def encode(tag: str) -> str:
    return fr'{tag}'
