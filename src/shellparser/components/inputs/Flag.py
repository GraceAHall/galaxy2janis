
from __future__ import annotations
from typing import Any, Optional
from gx.xmltool.param.InputParam import BoolParam

from shellparser.components.CommandComponent import BaseCommandComponent
from gx.xmltool.param.Param import Param


class Flag(BaseCommandComponent):
    def __init__(self, prefix: str, name: Optional[str]=None) -> None:
        super().__init__()
        self.prefix = prefix

    @property
    def name(self) -> str:
        return self.prefix.strip('--')

    @property
    def default_value(self) -> bool:
        if self.gxparam:
            return self.get_default_from_gxparam()
        else:
            return self.get_default_from_presence()
    
    def get_default_from_gxparam(self) -> bool:
        if isinstance(self.gxparam, BoolParam):
            if self.gxparam.checked and self.gxparam.truevalue == self.prefix:
                return True
            elif self.gxparam.checked and self.gxparam.truevalue == "":
                return False
            elif not self.gxparam.checked and self.gxparam.falsevalue == self.prefix:
                return True
            elif not self.gxparam.checked and self.gxparam.falsevalue == "":
                return False
        return False
    
    def get_default_from_presence(self) -> bool:
        if all([self.presence_array]):
            return True
        return False
   
    @property
    def optional(self) -> bool:
        return True

    @property
    def array(self) -> bool:
        return False

    @property
    def docstring(self) -> Optional[str]:
        if self.gxparam:
            return self.gxparam.docstring
        return None

    def update(self, incoming: Any):
        assert(isinstance(incoming, Flag))
        # gxparam transfer
        if not self.gxparam and incoming.gxparam:
            self.gxparam: Optional[Param] = incoming.gxparam
        # presence
        cmdstr_index = len(incoming.presence_array) - 1
        self.update_presence_array(cmdstr_index)
        
    def __str__(self) -> str:
        return f'{str(self.default_value):20}{str(self.optional):>10}'
