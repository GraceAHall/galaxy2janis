



from __future__ import annotations
from command.components.CommandComponent import BaseCommandComponent
from typing import Any, Optional
from xmltool.param.OutputParam import DataOutputParam, CollectionOutputParam
from xmltool.param.Param import Param


class WildcardOutput(BaseCommandComponent):
    def __init__(self, gxparam: Param):
        super().__init__()
        self.gxparam = gxparam
        assert(self.gxparam)

    def get_name(self) -> str:
        if self.gxparam:
            return self.gxparam.name
        raise RuntimeError('an WildcardOutput must have a gxparam')

    def get_default_value(self) -> Any:
        raise NotImplementedError()
    
    def is_optional(self) -> bool:
        # NOTE - janis does not allow optional outputs
        return False

    def is_array(self) -> bool:
        match self.gxparam:
            case CollectionOutputParam() | DataOutputParam():
                return self.gxparam.is_array()
            case _:
                pass
        return False
   
    def get_docstring(self) -> Optional[str]:
        if self.gxparam:
            return self.gxparam.get_docstring()
        return 'output created during runtime. file is collected from working directory'

    def update(self, incoming: Any):
        pass


