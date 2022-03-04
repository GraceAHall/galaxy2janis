
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from tool.param.InputParam import SelectParam

from tool.param.Param import Param
from command.components.ValueRecord import OptionValueRecord
from command.components.CommandComponent import BaseCommandComponent


@dataclass
class Option(BaseCommandComponent):
    prefix: str
    value: list[str]
    delim: str = ' '
    gxvar: Optional[Param] = None
    gxvar_attachment: int = 1
    stage: str = 'pre_options'
    presence_array: list[bool] = field(default_factory=list)

    def __post_init__(self):
        self.value_record: OptionValueRecord = OptionValueRecord()
        self.value_record.add(self.value)

    def update(self, incoming: Option):
        # transfer values
        for obsval in incoming.value_record.record:
            self.value_record.add(obsval)
        # transfer galaxy param reference
        if not self.gxvar and incoming.gxvar:
            self.gxvar = incoming.gxvar
        # presence
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
        if self.gxvar:
            if isinstance(self.gxvar, SelectParam):
                if self.gxvar.multiple:
                    return True
        return False

    def get_docstring(self) -> Optional[str]:
        if self.gxvar:
            return self.gxvar.get_docstring()
        return f'examples: {", ".join(self.value_record.get_unique_values()[:3])}'

    def __str__(self) -> str:
        return f'{str(self.prefix):30}{str(self.get_default_value()):20}{str(self.is_optional()):>10}'


