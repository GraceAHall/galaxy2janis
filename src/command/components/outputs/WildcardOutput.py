



from __future__ import annotations
from command.components.CommandComponent import BaseCommandComponent
from typing import Any, Optional
from xmltool.param.OutputParam import DataOutputParam, CollectionOutputParam


class WildcardOutput(BaseCommandComponent):
    def __init__(self):
        super().__init__()
        self.verified: bool = False

    @property
    def name(self) -> str:
        if self.gxparam:
            return self.gxparam.name
        raise RuntimeError('an WildcardOutput must have a gxparam')

    @property
    def default_value(self) -> str:
        return self.gxparam.wildcard_pattern
    
    @property
    def optional(self) -> bool:
        # NOTE - janis does not allow optional outputs
        return False

    @property
    def array(self) -> bool:
        match self.gxparam:
            case CollectionOutputParam() | DataOutputParam():
                return self.gxparam.array
            case _:
                pass
        return False
   
    @property
    def docstring(self) -> Optional[str]:
        if self.gxparam:
            return self.gxparam.docstring
        return 'output created during runtime. file is collected from working directory'

    def update(self, incoming: Any):
        pass


