
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from xmltool.param.Param import Param
from command.components.CommandComponent import BaseCommandComponent
from datatypes.conversion import cast_gx_to_janis
from datatypes.JanisDatatype import JanisDatatype


@dataclass
class Flag(BaseCommandComponent):
    prefix: str
    cmd_pos: int = -1
    gxvar: Optional[Param] = None
    stage: str = 'pre_options'
    presence_array: list[bool] = field(default_factory=list)

    def get_name(self) -> str:
        return self.prefix.strip('--').lower().replace('-', '_')

    def get_default_value(self) -> str:
        if self.gxvar:
            default = self.gxvar.get_default()
            if self.prefix in default:
                return str(True)
        return str(False)

    def get_janis_datatypes(self) -> list[JanisDatatype]:
        return [cast_gx_to_janis('boolean')]
    
    def is_optional(self) -> bool:
        return True

    def is_array(self) -> bool:
        return False

    def is_stdout(self) -> bool:
        return False

    def get_docstring(self) -> Optional[str]:
        if self.gxvar:
            return self.gxvar.get_docstring()
        return None

    def update(self, incoming: Flag):
        # gxvar transfer
        if not self.gxvar and incoming.gxvar:
            self.gxvar = incoming.gxvar
        # presence
        cmdstr_index = len(incoming.presence_array) - 1
        self.update_presence_array(cmdstr_index)
        
    def __str__(self) -> str:
        return f'{str(self.get_default_value()):20}{str(self.is_optional()):>10}'
