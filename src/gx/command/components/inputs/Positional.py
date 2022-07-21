


from __future__ import annotations
from typing import Any, Optional

from ..ValueRecord import ValueRecord
from .InputComponent import InputComponent
from . import utils

from gx.gxtool.param.Param import Param


class Positional(InputComponent):
    def __init__(self) -> None:
        super().__init__()
        self.before_opts: bool = False
        self.values: ValueRecord = ValueRecord()

    @property
    def name(self) -> str:
        # get name from galaxy param if available
        if self.gxparam:
            return self.gxparam.name
        # otherwise, most commonly witnessed option value as name
        pseudo_name = self.values.most_common_value
        if not pseudo_name:
            pseudo_name = 'positional'
        return pseudo_name.strip('$')
    
    @property
    def default_value(self) -> Any:
        """gets the default value for this component"""
        if self.gxparam:
            default = self.gxparam.default
        elif self.values.env_var:
            default = self.values.env_var
        else:
            default = self.values.most_common_value
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
        #return f'examples: {", ".join(self.values.unique[:3])}'

    def update(self, incoming: Any) -> None:
        # transfer values
        assert(isinstance(incoming, Positional))
        self.values.record += incoming.values.record
        # transfer galaxy param reference
        if not self.gxparam and incoming.gxparam:
            self.gxparam: Optional[Param] = incoming.gxparam

    def has_single_value(self) -> bool:
        if len(self.values.counts) == 1:
            return True
        return False
    
    def __str__(self) -> str:
        return f'{str(self.default_value):20}{str(self.optional):>10}'
