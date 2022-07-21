

from typing import Any
from gx.command.components import InputComponent
from .groups import TagGroup

groups: dict[str, TagGroup] = {}


def register(entity: Any) -> None:  
    """register a tag in the active TagGroup"""
    group = _get_active()
    starting_text = _get_starting_text(entity)
    group.register(starting_text, entity) 

def get(uuid: str) -> str:
    """get a tag from any TagGroup"""
    global groups
    for group in groups.values():
        tag = group.get(uuid)
        if tag:
            return tag
    raise RuntimeError('No tag registered')

def new_group(section: str, uuid: str):
    """
    create new TagGroup (ie for a new workflow or tool), 
    then switch to that TagGroup to start registering tags
    """
    global groups
    groups[uuid] = TagGroup(section)
    switch_group(uuid)

def switch_group(uuid: str):
    """swap to a specific TagGroup to register new tags in that group"""
    _clear_active()
    _set_active(uuid)
            


def _get_active() -> TagGroup:
    global groups
    for group in groups.values():
        if group.active:
            return group
    raise RuntimeError('no active group')

def _set_active(query_uuid: str):
    global groups
    for uuid, group in groups.items():
        if uuid == query_uuid:
            group.active = True
            return
    raise RuntimeError('group doesnt exist')

def _clear_active():
    global groups
    for group in groups.values():
        group.active = False

def _get_starting_text(entity: Any) -> str:
    group = _get_active()
    if group.section == 'workflow':
        return _get_starting_text_wflow(entity)
    elif group.section == 'tool':
        return _get_starting_text_tool(entity)
    else:
        raise RuntimeError()

def _get_starting_text_wflow(entity: Any) -> str:
    match entity.__class__.__name__:
        case 'Workflow':
            return entity.metadata.name
        case 'WorkflowInput':
            if not entity.is_runtime:
                return f'in_{entity.name}'
            else:
                return entity.name
        case 'WorkflowStep':
            if entity.metadata.label:
                return entity.metadata.label
            elif entity.metadata.step_name:
                return entity.metadata.step_name
            else:
                return entity.metadata.wrapper.tool_name
        case _:
            raise RuntimeError(f'cannot register a {entity.__class__.__name__}')

def _get_starting_text_tool(entity: Any) -> str:
    match entity.__class__.__name__:
        case 'Tool':
            return entity.metadata.id
        case 'Positional' | 'Flag' | 'Option':
            return _get_tool_input_name(entity)
        case 'RedirectOutput' | 'WildcardOutput' | 'InputOutput':
            basetag = entity.name
            if basetag.startswith('out'):
                return basetag
            else:
                return f'out_{basetag}'
        case _:
            raise RuntimeError(f'cannot register a {entity.__class__.__name__}')

def _get_tool_input_name(component: InputComponent) -> str:
    default_name = component.name
    if default_name.isnumeric() and component.gxparam:
        return component.gxparam.name.rsplit('.', 1)[-1]  # adv.reference -> reference (gxvarnames)
    return default_name

