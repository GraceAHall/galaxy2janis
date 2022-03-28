
from __future__ import annotations
from typing import Optional
from datatypes.JanisDatatype import JanisDatatype
from xmltool.param.InputParam import SelectParam

from xmltool.param.Param import Param
from command.components.ValueRecord import OptionValueRecord
from command.components.CommandComponent import BaseCommandComponent

class Option(BaseCommandComponent):
    def __init__(self, prefix: str, values: list[str], epath_id: int, delim: str) -> None:
        self.prefix = prefix
        self.values = values
        self.epath_id = epath_id
        self.delim = delim
        self.cmd_pos: int = -1
        self.gxparam: Optional[Param] = None
        self.gxparam_attachment: int = 1
        self.presence_array: list[bool] = []
        self.janis_datatypes: list[JanisDatatype] = []
        self.value_record: OptionValueRecord = OptionValueRecord()
        self.value_record.add(self.epath_id, self.values)

    def get_name(self) -> str:
        return self.prefix.strip('--').lower().replace('-', '_')

    def get_default_value(self) -> Optional[str]:
        # get default from galaxy param if available
        if self.gxparam:
            return self.gxparam.get_default()
        # otherwise, most commonly witnessed option value
        return self.value_record.get_most_common_value()
        
    def is_optional(self) -> bool:
        if all(self.presence_array):
            return False
        return True

    def is_array(self) -> bool:
        if self.gxparam:
            if isinstance(self.gxparam, SelectParam):
                if self.gxparam.multiple:
                    return True
        return False

    def get_docstring(self) -> Optional[str]:
        if self.gxparam:
            return self.gxparam.get_docstring()
        return f'examples: {", ".join(self.value_record.get_unique_values()[:3])}'

    def update(self, incoming: Option):
        # transfer values
        self.value_record.record += incoming.value_record.record
        # transfer galaxy param reference
        if not self.gxparam and incoming.gxparam:
            self.gxparam = incoming.gxparam
        # presence
        cmdstr_index = len(incoming.presence_array) - 1
        self.update_presence_array(cmdstr_index)

    def __str__(self) -> str:
        return f'{str(self.prefix):30}{str(self.get_default_value()):20}{str(self.is_optional()):>10}'


