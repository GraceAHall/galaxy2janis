



from __future__ import annotations
from command.components.CommandComponent import BaseCommandComponent
from typing import Optional
from xmltool.param.OutputParam import DataOutputParam, CollectionOutputParam


class UncertainOutput(BaseCommandComponent):

    def get_name(self) -> str:
        if self.gxparam:
            return self.gxparam.name
        raise RuntimeError('an UnknownOutput must have a gxparam')

    def get_default_value(self) -> str:
        return '__UNKNOWN_OUTPUT__'
    
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

    def update(self, incoming: UncertainOutput) -> None:
        raise NotImplementedError()


