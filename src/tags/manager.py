


from abc import ABC, abstractmethod
from typing import Any
from .groups import TagGroup



class TagManager(ABC):

    @abstractmethod
    def register(self, entity: Any) -> None:
        ...
    
    @abstractmethod
    def get(self, uuid: str) -> None:
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
        group = TagGroup(subtype='tool')
        self.groups.append(group)

    def register(self, entity: Any) -> None:
        group = self.active_group
        group.register(entity) 
    
    def get(self, uuid: str) -> str:
        for group in self.groups:
            tag = group.get(uuid)
            if tag:
                return tag
        raise RuntimeError('No tag registered')


class WorkflowTagManager(TagManager):
    def __init__(self):
        self.group = TagGroup(subtype='workflow')

    def register(self, entity: Any) -> None:
        self.group.register(entity)
    
    def get(self, uuid: str) -> str:
        tag = self.group.get(uuid)
        if tag:
            return tag
        else:
            raise RuntimeError('No tag registered')

