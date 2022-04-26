
from __future__ import annotations
from typing import Any, Optional
from xmltool.param.InputParam import SelectParam

from command.components.ValueRecord import OptionValueRecord
from command.components.CommandComponent import BaseCommandComponent


class Option(BaseCommandComponent):
    def __init__(self, prefix: str, values: list[str], delim: str) -> None:
        super().__init__()
        self.prefix = prefix
        self.delim = delim
        self.gxparam_attachment: int = 1
        self.value_record: OptionValueRecord = OptionValueRecord()
        self.value_record.add(values)

    def get_name(self) -> str:
        return self.prefix.strip('--')

    def get_default_value(self) -> Optional[Any]:
        """gets the default value for this component"""
        #if utils.datatypes_permit_default(self.janis_datatypes):
        default = None
        if self.gxparam:
            default = self.gxparam.get_default()
        if default is None:
            default = self.value_record.get_most_common_value(no_env=True)
        return default

        # if default is None and self.value_record.get_observed_env_var():
        #     default = self.value_record.get_observed_env_var()
        # if default is None:
        #     default = self.value_record.get_most_common_value()
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
        if self.gxparam:
            if isinstance(self.gxparam, SelectParam):
                if self.gxparam.multiple:
                    return True
        return False

    def get_docstring(self) -> Optional[str]:
        if self.gxparam:
            return self.gxparam.get_docstring()
        return ''
        #return f'examples: {", ".join(self.value_record.get_unique_values()[:3])}'

    def update(self, incoming: Any):
        assert(isinstance(incoming, Option))
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


