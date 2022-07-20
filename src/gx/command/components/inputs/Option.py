
from __future__ import annotations
from typing import Any, Optional

from gx.gxtool.param.Param import Param

from ..ValueRecord import OptionValueRecord
from .InputComponent import InputComponent
from . import utils


class Option(InputComponent):
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
        if self.gxparam:
            default = self.gxparam.default
        else:
            default = self.value_record.get_most_common_value()
        return utils.sanitise_default_value(default)
    
    @property
    def optional(self) -> bool:
        if self.forced_optionality is not None:
            return self.forced_optionality
        elif self.gxparam:
            return self.gxparam.optional
        return False

    @property
    def array(self) -> bool:
        if self.forced_array is not None:
            return self.forced_array
        elif self.gxparam:
            return self.gxparam.array
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

    def __str__(self) -> str:
        return f'{str(self.prefix):30}{str(self.default_value):20}{str(self.optional):>10}'


