



from __future__ import annotations
from .OutputComponent import OutputComponent
from typing import Optional


class WildcardOutput(OutputComponent):
    def __init__(self):
        super().__init__()
        self.verified: bool = False

    @property
    def name(self) -> str:
        if self.gxparam:
            return self.gxparam.name
        raise RuntimeError('a WildcardOutput must have a gxparam')

    @property
    def optional(self) -> bool:
        # NOTE - janis does not allow optional outputs
        return False
   
    @property
    def docstring(self) -> Optional[str]:
        if self.gxparam:
            return self.gxparam.docstring
        return 'output created during runtime. file is collected from working directory'



