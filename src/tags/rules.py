

from typing import Any
import keyword
import builtins

import runtime.logging.logging as logging


python_keys = set(keyword.kwlist)
builtin_keys = set(dir(builtins))
janis_keys = set([
    "identifier",
    "tool",
    "scatter",
    "ignore_missing",
    "output",
    "outputs",
    "input",
    "inputs"
])
keywords = python_keys | builtin_keys | janis_keys


def replace_keywords(tag: str, entity: Any) -> str:
    if tag in keywords:
        tag = _append_datatype(tag, entity)
    return tag

def encode(tag: str) -> str:
    return fr'{tag}'

def numeric(tag: str, entity: Any) -> str:
    """
    if tag is just a number, prepend the component type. 
    """
    if tag.replace('.','',1).isnumeric():  
        tag = _prepend_component_type(entity.cmd_pos, entity)
    return tag

def numeric_start(tag: str, entity: Any) -> str:
    """
    if tag starts with a number, prepend the component type. 
    """
    if len(tag) > 0 and tag[0].isnumeric():
        tag = _prepend_component_type(tag, entity)
    return tag

def short_tag(tag: str, entity: Any) -> str:
    if len(tag) == 0:
        logging.zero_length_tag()
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
    tag = tag.replace('*', '')
    tag = tag.replace('(', '')
    tag = tag.replace(')', '')
    tag = tag.replace(']', '')
    tag = tag.replace('[', '')
    tag = tag.replace('.', '_')
    tag = tag.replace(' ', '_')
    tag = tag.replace('|', '_')
    tag = tag.replace('/', '_')
    tag = tag.replace('\\', '_')
    tag = tag.replace('"', '')
    tag = tag.replace("'", '')
    tag = tag.replace("@", 'at')
    return tag

def _prepend_component_type(tag: str, entity: Any) -> str:
    entity_type: str = entity.__class__.__name__
    entity_type = entity_type.lower()
    return f'{entity_type}_{tag}'

def _append_datatype(tag: str, entity: Any) -> str:
    dtype = entity.janis_datatypes[0].classname.lower()
    if not tag.endswith(dtype): # don't add the dtype if its already been added
        tag = f"{tag}_{dtype}"
    return tag

def _strip_numerals(tag: str) -> str:  # ??? y
    return tag.lstrip('0123456789')

