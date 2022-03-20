



from __future__ import annotations
from command.components.CommandComponent import BaseCommandComponent
from typing import Any, Optional
from xmltool.param.OutputParam import DataOutputParam, CollectionOutputParam
from xmltool.param.Param import Param
from datatypes.JanisDatatype import JanisDatatype


class WildcardOutput(BaseCommandComponent):
    def __init__(self, gxparam: Param):
        self.gxparam = gxparam
        self.presence_array: list[bool] = []  # this makes no sense
        self.datatypes: list[JanisDatatype] = []

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

    def update(self, incoming: WildcardOutput):
        pass

    def get_selector_str(self) -> str:
        if self.gxparam and self.gxparam.wildcard_pattern:  # type: ignore
            return f'WildcardSelector("{self.gxparam.wildcard_pattern}")'  # type: ignore
        else:
            raise RuntimeError()

