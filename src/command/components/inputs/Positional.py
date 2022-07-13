


from __future__ import annotations
from typing import Any, Optional

from ..ValueRecord import PositionalValueRecord
from .InputComponent import InputComponent

from gx.gxtool.param.Param import Param
import shellparser.regex.scanners as scanners


class Positional(InputComponent):
    def __init__(self, value: str) -> None:
        super().__init__()
        self.before_opts: bool = False
        self.value_record: PositionalValueRecord = PositionalValueRecord()
        self.value_record.add(value)

    @property
    def name(self) -> str:
        # get name from galaxy param if available
        if self.gxparam:
            return self.gxparam.name
        # otherwise, most commonly witnessed option value as name
        pseudo_name = self.value_record.get_most_common_value()
        if not pseudo_name:
            pseudo_name = 'positional'
        return pseudo_name.strip('$')
    
    @property
    def default_value(self) -> Any:
        """gets the default value for this component"""
        #if utils.datatypes_permit_default(self.janis_datatypes):
        if self.gxparam:
            default = self.gxparam.default
        elif self.value_record.get_observed_env_var():
            default = self.value_record.get_observed_env_var()
        else:
            default = self.value_record.get_most_common_value()
        return default
        #return utils.sanitise_default_value(default)

    @property
    def optional(self) -> bool:
        if self.forced_optionality is not None:
            return self.forced_optionality
        elif self.gxparam: 
            return self.gxparam.optional
        return True

    @property
    def array(self) -> bool:
        return False
    
    @property
    def docstring(self) -> Optional[str]:
        if self.gxparam:
            return self.gxparam.docstring
        return ''
        #return f'examples: {", ".join(self.value_record.get_unique_values()[:3])}'

    def update(self, incoming: Any) -> None:
        # transfer values
        assert(isinstance(incoming, Positional))
        self.value_record.record += incoming.value_record.record
        # transfer galaxy param reference
        if not self.gxparam and incoming.gxparam:
            self.gxparam: Optional[Param] = incoming.gxparam

    def has_single_value(self) -> bool:
        counts = self.value_record.get_counts()
        if len(counts) == 1:
            return True
        return False
    
    def values_are_variables(self) -> bool:
        str_values = self.value_record.unique_values
        for val in str_values:
            if not scanners.get_variables_fmt1(val) and not scanners.get_variables_fmt2(val):
                return False
        return True

    def __str__(self) -> str:
        return f'{str(self.default_value):20}{str(self.optional):>10}'


