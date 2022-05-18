


from __future__ import annotations
from typing import Any, Optional
from command.components.ValueRecord import PositionalValueRecord
from command.components.CommandComponent import BaseCommandComponent
#import command.components.inputs.utils as utils
import command.text.regex.scanners as scanners
from xmltool.param.Param import Param

class Positional(BaseCommandComponent):
    def __init__(self, value: str) -> None:
        super().__init__()
        self.before_opts: bool = False
        self.value_record: PositionalValueRecord = PositionalValueRecord()
        self.value_record.add(value)

    def get_name(self) -> str:
        # get name from galaxy param if available
        if self.gxparam:
            return self.gxparam.name
        # otherwise, most commonly witnessed option value as name
        pseudo_name = self.value_record.get_most_common_value()
        if not pseudo_name:
            pseudo_name = 'positional'
        return pseudo_name.strip('$')
    
    def get_default_value(self) -> Any:
        """gets the default value for this component"""
        #if utils.datatypes_permit_default(self.janis_datatypes):
        if self.gxparam:
            default = self.gxparam.get_default()
        elif self.value_record.get_observed_env_var():
            default = self.value_record.get_observed_env_var()
        else:
            default = self.value_record.get_most_common_value()
        return default
        #return utils.sanitise_default_value(default)

    def is_optional(self) -> bool:
        if self.forced_optionality is not None:
            return self.forced_optionality
        elif self.gxparam and self.gxparam.is_optional():
            return True
        elif all(self.presence_array):
            return False
        return True

    def is_array(self) -> bool:
        return False
    
    def get_docstring(self) -> Optional[str]:
        if self.gxparam:
            return self.gxparam.get_docstring()
        return ''
        #return f'examples: {", ".join(self.value_record.get_unique_values()[:3])}'

    def update(self, incoming: Any) -> None:
        # transfer values
        assert(isinstance(incoming, Positional))
        self.value_record.record += incoming.value_record.record
        # transfer galaxy param reference
        if not self.gxparam and incoming.gxparam:
            self.gxparam: Optional[Param] = incoming.gxparam
        # update presence
        cmdstr_index = len(incoming.presence_array) - 1
        self.update_presence_array(cmdstr_index)
    
    def has_single_value(self) -> bool:
        counts = self.value_record.get_counts()
        if len(counts) == 1:
            return True
        return False
    
    def values_are_variables(self) -> bool:
        str_values = self.value_record.get_unique_values()
        for val in str_values:
            if not scanners.get_variables_fmt1(val) and not scanners.get_variables_fmt2(val):
                return False
        return True

    def __str__(self) -> str:
        return f'{str(self.get_default_value()):20}{str(self.is_optional()):>10}'


