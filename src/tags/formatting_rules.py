

from typing import Any

from command.components.inputs.Positional import Positional
from command.components.inputs.Flag import Flag
from command.components.inputs.Option import Option

# from command.components.outputs.InputOutput import InputOutput
# from command.components.outputs.RedirectOutput import RedirectOutput
# from command.components.outputs.WildcardOutput import WildcardOutput
#OutputComponent = InputOutput | RedirectOutput | WildcardOutput



def encode(tag: str) -> str:
    return fr'{tag}'

def numeric(tag: str, entity: Any) -> str:
    if tag.replace('.','',1).isnumeric():  # removes '.' then checks if all chars are digits
        match entity:
            case Positional():
                tag = f'positional_{entity.cmd_pos}'
            case Flag() | Option():
                tag = _prepend_component_type(tag, entity)
            case _:
                pass
    return tag

def numeric_start(tag: str, entity: Any) -> str:
    if tag[0].isnumeric():
        tag = _prepend_component_type(tag, entity)
    return tag

def short_tag(tag: str, entity: Any) -> str:
    if len(tag) == 0:
        tag = _prepend_component_type(tag, entity)
        tag = f'{tag}ERROR'
    elif len(tag) == 1:
        tag = _prepend_component_type(tag, entity)
    return tag

def capitalisation(tag: str, entity: Any) -> str:
    # if single letter allow any capitalisation, otherwise lower
    # this doesn't really work at the moment as will always lower, due
    # to the short_tag() rule
    if len(tag) > 1:
        return tag.lower()
    else:
        return tag[0]

def non_alphanumeric(tag: str, entity: Any) -> str:
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

def prohibited_key(tag: str, entity: Any) -> str:
    if tag in prohibited_keys:
        tag = _append_datatype(tag, entity)
    return tag

# def _standardise_numeric(tag: str) -> str:
#     pass

def _strip_numerals(tag: str) -> str:
    return tag.lstrip('0123456789')

def _prepend_component_type(tag: str, entity: Any) -> str:
    match entity:
        case Positional():
            tag = f'input_{tag}'
        case Flag():
            tag = f'flag_{tag}'
        case Option():
            tag = f'option_{tag}'
        case _:
            pass
            ## if isinstance(entity, OutputComponent):
            #     tag = f'out_{tag}'
    return tag

def _append_datatype(tag: str, entity: Any) -> str:
    dtype = entity.janis_datatypes[0].classname.lower()
    if not tag.endswith(dtype): # don't add the dtype if its already been added
        tag = f"{tag}_{dtype}"
    return tag


