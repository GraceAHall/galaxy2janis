
from __future__ import annotations
from typing import Optional

from tool.param.Param import Param
from command.components.ObservedValueRecord import ObservedValueRecord, ObservedValue


class Option:
    def __init__(self, prefix: str, value: str, cmdstr_index: int, delim: str=' ', gxvar_attachment: int=1):
        self.prefix = prefix
        self.delim: str = delim
        self.gxvar_attachment = gxvar_attachment
        self.value_record: ObservedValueRecord = ObservedValueRecord()
        self.value_record.update(ObservedValue(value, cmdstr_index))
        
        self.gxvar: Optional[Param] = None
        self.presence_array: list[bool] = []
        self.cmd_pos: int = 0
        self.update_presence_array(cmdstr_index)

    def update(self, incoming: Option):
        # cmdstr presence
        cmdstr_index = len(incoming.presence_array) # NOTE shitty work around
        self.update_presence_array(cmdstr_index)
        # values
        for obsval in incoming.value_record.record:
            self.value_record.update(obsval)
        # galaxy param reference
        if not self.gxvar and incoming.gxvar:
            self.gxvar = incoming.gxvar

    def update_presence_array(self, cmdstr_index: int, fill_false: bool=False):
        # ensure presence array is filled in to current cmdstr
        while len(self.presence_array) < cmdstr_index - 1:
            self.presence_array.append(False)
        
        # now that component is up to date
        presence = False if fill_false else True
        self.presence_array.append(presence)

    def get_default_value(self) -> Optional[str]:
        # galaxy param if available
        if self.gxvar:
            return self.gxvar.get_default()
        # otherwise, most commonly witnessed option value
        return self.value_record.get_most_common_value()
        
    def is_optional(self) -> bool:
        raise NotImplementedError

    def is_array(self) -> bool:
        # yes, this is possible to work out (using the galaxy param)
        raise NotImplementedError

