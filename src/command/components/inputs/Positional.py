


from __future__ import annotations
from typing import Optional
from datatypes.JanisDatatype import JanisDatatype
from xmltool.param.Param import Param
from command.components.ValueRecord import PositionalValueRecord
from command.components.CommandComponent import BaseCommandComponent
import command.components.inputs.utils as utils


class Positional(BaseCommandComponent):
    def __init__(self, value: str, epath_id: int) -> None:
        self.value = value
        self.epath_id = epath_id
        self.cmd_pos: int = -1
        self.before_opts: bool = False
        self.gxparam: Optional[Param] = None
        self.presence_array: list[bool] = []
        self.janis_datatypes: list[JanisDatatype] = []
        self.value_record: PositionalValueRecord = PositionalValueRecord()
        self.value_record.add(self.epath_id, self.value)

    def get_name(self) -> str:
        # get name from galaxy param if available
        if self.gxparam:
            return self.gxparam.name
        # otherwise, most commonly witnessed option value as name
        pseudo_name = self.value_record.get_most_common_value()
        return pseudo_name.strip('$')
    
    def get_default_value(self) -> str:
        """gets the default value for this component"""
        if utils.datatypes_permit_default(self.janis_datatypes):
            if self.gxparam:
                default = self.gxparam.get_default()
            else:
                default = self.value_record.get_most_common_value()
        return utils.sanitise_default_value(default)

    def is_optional(self) -> bool:
        if all(self.presence_array):
            return False
        return True

    def is_array(self) -> bool:
        return False
    
    def get_docstring(self) -> Optional[str]:
        if self.gxparam:
            return self.gxparam.get_docstring()
        return ''
        #return f'examples: {", ".join(self.value_record.get_unique_values()[:3])}'

    def update(self, incoming: Positional) -> None:
        # transfer values
        self.value_record.record += incoming.value_record.record
        # transfer galaxy param reference
        if not self.gxparam and incoming.gxparam:
            self.gxparam = incoming.gxparam
        # update presence
        cmdstr_index = len(incoming.presence_array) - 1
        self.update_presence_array(cmdstr_index)
    
    def has_single_value(self) -> bool:
        counts = self.value_record.get_counts()
        if len(counts) == 1:
            return True
        return False

    def __str__(self) -> str:
        return f'{str(self.get_default_value()):20}{str(self.is_optional()):>10}'


