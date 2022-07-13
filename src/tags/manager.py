


from abc import ABC, abstractmethod
from typing import Any

from command import InputComponent
from .groups import TagGroup



class TagManager(ABC):
    permitted: set[str]

    @abstractmethod
    def register(self, entity: Any) -> None:
        ...
    
    @abstractmethod
    def get(self, uuid: str) -> str:
        ...
    
    @abstractmethod
    def _get_starting_text(self, entity: Any) -> str:
        ...


class ToolTagManager(TagManager):
    def __init__(self):
        self.groups: list[TagGroup] = []
    
    @property
    def active_group(self) -> TagGroup:
        if not self.groups:
            raise RuntimeError('please add tool group with new_tool()')
        return self.groups[-1]
    
    def new_tool(self):
        group = TagGroup()
        self.groups.append(group)

    def register(self, entity: Any) -> None:
        group = self.active_group
        starting_text = self._get_starting_text(entity)
        group.register(starting_text, entity) 
    
    def get(self, uuid: str) -> str:
        for group in self.groups:
            tag = group.get(uuid)
            if tag:
                return tag
        raise RuntimeError('No tag registered')
    
    def _get_starting_text(self, entity: Any) -> str:
        match entity.__class__.__name__:
            case 'Tool':
                return entity.metadata.id
            case 'Positional' | 'Flag' | 'Option':
                return self._get_tool_input_name(entity)
            case 'RedirectOutput' | 'WildcardOutput' | 'InputOutput':
                basetag = entity.name
                if basetag.startswith('out'):
                    return basetag
                else:
                    return f'out_{basetag}'
            case _:
                raise RuntimeError(f'cannot register a {entity.__class__.__name__}')
    
    def _get_tool_input_name(self, component: InputComponent) -> str:
        default_name = component.name
        if default_name.isnumeric() and component.gxparam:
            return component.gxparam.name.rsplit('.', 1)[-1]  # adv.reference -> reference (gxvarnames)
        return default_name


class WorkflowTagManager(TagManager):
    def __init__(self):
        self.group = TagGroup()

    def register(self, entity: Any) -> None:
        starting_text = self._get_starting_text(entity)
        self.group.register(starting_text, entity)
    
    def get(self, uuid: str) -> str:
        tag = self.group.get(uuid)
        if tag:
            return tag
        else:
            raise RuntimeError('No tag registered')

    def _get_starting_text(self, entity: Any) -> str:
        match entity.__class__.__name__:
            case 'Workflow':
                return entity.metadata.name
            case 'WorkflowInput':
                if entity.is_galaxy_input_step:
                    return f'in_{entity.name}'
                else:
                    return entity.name
            case 'WorkflowStep':
                return entity.metadata.wrapper.tool_id
            case 'StepOutput':
                step_tag = self.get(entity.step_uuid)
                out_name = entity.tool_output.name
                return f'{step_tag}.{out_name}'
            case _:
                raise RuntimeError(f'cannot register a {entity.__class__.__name__}')
