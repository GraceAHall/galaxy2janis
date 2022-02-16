
from __future__ import annotations
from typing import Optional

from tool.param.Param import Param


class Flag:
    def __init__(self, prefix: str, cmdstr_index: int):
        self.prefix = prefix
        self.galaxy_object: Optional[Param] = None
        self.presence_array: list[bool] = []
        self.cmd_pos: int = 0
        self.update_presence_array(cmdstr_index)

    def update(self, incoming: Flag, cmdstr_index: int):
        self.update_presence_array(cmdstr_index)
        if not self.galaxy_object and incoming.galaxy_object:
            self.galaxy_object = incoming.galaxy_object

    def update_presence_array(self, cmdstr_index: int, fill_false: bool=False):
        # ensure presence array is filled in to current cmdstr
        while len(self.presence_array) < cmdstr_index - 1:
            self.presence_array.append(False)
        
        # now that component is up to date
        presence = False if fill_false else True
        self.presence_array.append(presence)

    def get_default_value(self) -> str:
        return self.prefix
    
    def is_optional(self) -> bool:
        return True

    def is_array(self) -> bool:
        return False
