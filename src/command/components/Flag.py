
from __future__ import annotations
from typing import Optional

from tool.param.Param import Param


class Flag:
    def __init__(self, prefix: str, cmdstr_index: int, gxvar: Optional[Param]=None):
        self.prefix = prefix
        self.gxvar = gxvar
        self.presence_array: list[bool] = []
        self.cmd_pos: int = 0
        self.update_presence_array(cmdstr_index)

    def update(self, incoming: Flag):
        cmdstr_index = len(incoming.presence_array) # NOTE shitty work around
        self.update_presence_array(cmdstr_index)
        if not self.gxvar and incoming.gxvar:
            self.gxvar = incoming.gxvar

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
