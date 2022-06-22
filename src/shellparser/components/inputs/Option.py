
from __future__ import annotations
from typing import Any, Optional
from gx.xmltool.param.InputParam import SelectParam

from shellparser.components.ValueRecord import OptionValueRecord
from shellparser.components.CommandComponent import BaseCommandComponent
from gx.xmltool.param.Param import Param


class Option(BaseCommandComponent):
    def __init__(self, prefix: str, values: list[str], delim: str) -> None:
        super().__init__()
        self.prefix = prefix
        self.delim = delim
        self.gxparam_attachment: int = 1
        self.value_record: OptionValueRecord = OptionValueRecord()
        self.value_record.add(values)

    @property
    def name(self) -> str:
        return self.prefix.strip('--')

    @property
    def default_value(self) -> Any:
        """gets the default value for this component"""
        #if utils.datatypes_permit_default(self.janis_datatypes):
        default = None
        if self.gxparam:
            default = self.gxparam.default
        if default is None:
            default = self.value_record.get_most_common_value()
        return default
    
    @property
    def optional(self) -> bool:
        if self.forced_optionality is not None:
            return self.forced_optionality
        elif self.gxparam and self.gxparam.optional:
            return True
        elif all(self.presence_array):
            return False
        return True

    @property
    def array(self) -> bool:
        if self.gxparam:
            if isinstance(self.gxparam, SelectParam):
                if self.gxparam.multiple:
                    return True
        return False

    @property
    def docstring(self) -> Optional[str]:
        if self.gxparam:
            return self.gxparam.docstring
        return ''
        #return f'examples: {", ".join(self.value_record.get_unique_values()[:3])}'

    def update(self, incoming: Any):
        assert(isinstance(incoming, Option))
        # transfer values
        self.value_record.record += incoming.value_record.record
        # transfer galaxy param reference
        if not self.gxparam and incoming.gxparam:
            self.gxparam: Optional[Param] = incoming.gxparam
        # presence
        cmdstr_index = len(incoming.presence_array) - 1
        self.update_presence_array(cmdstr_index)

    def __str__(self) -> str:
        return f'{str(self.prefix):30}{str(self.default_value):20}{str(self.optional):>10}'


