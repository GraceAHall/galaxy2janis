



from __future__ import annotations
from command.components.CommandComponent import BaseCommandComponent
from typing import Optional
from xmltool.param.OutputParam import DataOutputParam, CollectionOutputParam


class UncertainOutput(BaseCommandComponent):

    @property
    def name(self) -> str:
        if self.gxparam:
            return self.gxparam.name
        raise RuntimeError('an UncertainOutput must have a gxparam')

    @property
    def default_value(self) -> str:
        return '__UNKNOWN_OUTPUT__'
    
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

    def update(self, incoming: UncertainOutput) -> None:
        raise NotImplementedError()


