


from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from tool.param.Param import Param
from command.components.ValueRecord import PositionalValueRecord
from command.components.CommandComponent import BaseCommandComponent


@dataclass
class Positional(BaseCommandComponent):
    value: str
    epath_id: int
    cmd_pos: int = 0
    before_opts: bool = False
    gxvar: Optional[Param] = None
    presence_array: list[bool] = field(default_factory=list)
    #stage: str = 'pre_options'

    def __post_init__(self):
        self.value_record: PositionalValueRecord = PositionalValueRecord()
        self.value_record.add(self.epath_id, self.value)

    def update(self, incoming: Positional):
        # transfer values
        self.value_record.record += incoming.value_record.record
        # transfer galaxy param reference
        if not self.gxvar and incoming.gxvar:
            self.gxvar = incoming.gxvar
        # update presence
        cmdstr_index = len(incoming.presence_array) - 1
        self.update_presence_array(cmdstr_index)

    def get_default_value(self) -> str:
        # get default from galaxy param if available
        if self.gxvar:
            return self.gxvar.get_default()
        # otherwise, most commonly witnessed option value
        return self.value_record.get_most_common_value()

    def get_name(self) -> str:
        # get name from galaxy param if available
        if self.gxvar:
            return self.gxvar.name
        # otherwise, most commonly witnessed option value as name
        pseudo_name = self.value_record.get_most_common_value()
        return pseudo_name.strip('$')

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
        return False
    
    def has_single_value(self) -> bool:
        counts = self.value_record.get_counts()
        if len(counts) == 1:
            return True
        return False
    
    def get_docstring(self) -> Optional[str]:
        if self.gxvar:
            return self.gxvar.get_docstring()
        return f'examples: {", ".join(self.value_record.get_unique_values()[:3])}'

    def __str__(self) -> str:
        return f'{str(self.get_default_value()):20}{str(self.is_optional()):>10}'


