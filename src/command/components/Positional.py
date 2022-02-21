


from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from tool.param.Param import Param
from command.components.ObservedValueRecord import ObservedValueRecord
from command.components.CommandComponent import BaseCommandComponent


@dataclass
class Positional(BaseCommandComponent):
    value: str
    cmd_pos: int = 0
    gxvar: Optional[Param] = None
    presence_array: list[bool] = field(default_factory=list)

    def __post_init__(self):
        self.value_record: ObservedValueRecord = ObservedValueRecord()
        self.value_record.add(self.value)

    def update(self, incoming: Positional):
        # transfer values
        for obsval in incoming.value_record.record:
            self.value_record.add(obsval)
        # transfer galaxy param reference
        if not self.gxvar and incoming.gxvar:
            self.gxvar = incoming.gxvar
        # update presence
        cmdstr_index = len(incoming.presence_array) - 1
        self.update_presence_array(cmdstr_index)

    def get_default_value(self) -> Optional[str]:
        # get default from galaxy param if available
        if self.gxvar:
            return self.gxvar.get_default()
        # otherwise, most commonly witnessed option value
        return self.value_record.get_most_common_value()

    def get_datatype(self) -> list[str]:
        if self.gxvar:
            return self.gxvar.datatypes
        elif self.value_record.values_are_ints():
            return ['Int']
        elif self.value_record.values_are_floats():
            return ['Int']
        return ['File']  # TODO what is the fallback type? 
        
    def is_optional(self) -> bool:
        if all(self.presence_array):
            return False
        return True

    def is_array(self) -> bool:
        raise NotImplementedError
    
    def has_unique_value(self) -> bool:
        counts = self.value_record.get_counts()
        if len(counts) == 1:
            return True
        return False

    def __str__(self) -> str:
        return f'{str(self.get_default_value()):20}{str(self.is_optional()):>10}'


