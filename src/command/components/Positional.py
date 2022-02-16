


from __future__ import annotations
from typing import Optional

from tool.param.Param import Param
from command.components.ObservedValueRecord import ObservedValueRecord, ObservedValue


class Positional:
    def __init__(self, value: str, cmdstr_index: int):
        self.is_after_options: bool = False
        self.value_record: ObservedValueRecord = ObservedValueRecord()
        self.value_record.update(ObservedValue(value, cmdstr_index))

        self.galaxy_object: Optional[Param] = None
        self.presence_array: list[bool] = []
        self.cmd_pos: int = 0
        self.update_presence_array(cmdstr_index)

    def update(self, incoming: Positional, cmdstr_index: int):
        # cmdstr presence
        self.update_presence_array(cmdstr_index)
        # values
        for obsval in incoming.value_record.record:
            self.value_record.update(obsval)
        # galaxy param reference
        if not self.galaxy_object and incoming.galaxy_object:
            self.galaxy_object = incoming.galaxy_object

    def update_presence_array(self, cmdstr_index: int, fill_false: bool=False):
        # ensure presence array is filled in to current cmdstr
        while len(self.presence_array) < cmdstr_index - 1:
            self.presence_array.append(False)
        
        # now that component is up to date
        presence = False if fill_false else True
        self.presence_array.append(presence)

    def get_default_value(self) -> Optional[str]:
        # galaxy param if available
        if self.galaxy_object:
            return self.galaxy_object.get_default()
        # otherwise, most commonly witnessed option value
        return self.value_record.get_most_common_value()
    
    def is_optional(self) -> bool:
        raise NotImplementedError

    def is_array(self) -> bool:
        raise NotImplementedError
    
    def has_unique_value(self) -> bool:
        counts = self.value_record.get_counts()
        if len(counts) == 1:
            return True
        return False
