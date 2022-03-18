
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from xmltool.param.Param import Param

from command.components.CommandComponent import BaseCommandComponent


@dataclass
class Flag(BaseCommandComponent):
    prefix: str
    cmd_pos: int = 0
    gxvar: Optional[Param] = None
    stage: str = 'pre_options'
    presence_array: list[bool] = field(default_factory=list)

    def update(self, incoming: Flag):
        # gxvar transfer
        if not self.gxvar and incoming.gxvar:
            self.gxvar = incoming.gxvar
        # presence
        cmdstr_index = len(incoming.presence_array) - 1
        self.update_presence_array(cmdstr_index)

    def get_default_value(self) -> str:
        return self.prefix

    def get_datatype(self) -> list[str]:
        return ['Boolean']
    
    def is_optional(self) -> bool:
        return True

    def is_array(self) -> bool:
        return False

    def get_docstring(self) -> Optional[str]:
        if self.gxvar:
            return self.gxvar.get_docstring()
        return None
        
    def __str__(self) -> str:
        return f'{str(self.get_default_value()):20}{str(self.is_optional()):>10}'
