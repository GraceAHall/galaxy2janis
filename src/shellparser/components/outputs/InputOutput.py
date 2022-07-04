

from __future__ import annotations
from .OutputComponent import OutputComponent

from typing import Any, Optional
from gx.xmltool.param.OutputParam import DataOutputParam, CollectionOutputParam
from shellparser.components.CommandComponent import CommandComponent


class InputOutput(OutputComponent):
    def __init__(self, input_component: CommandComponent):
        super().__init__()
        self.input_component = input_component
        self.gxparam = self.input_component.gxparam
        assert(self.gxparam)

    @property
    def name(self) -> str:
        if self.gxparam:
            return self.gxparam.name
        raise RuntimeError('an InputOutput must have an input_component with an attached gxparam')

    @property
    def default_value(self) -> Any:
        raise NotImplementedError()

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
        return f'output created during runtime. file relates to the {self.input_component.name} input'

    def update(self, incoming: Any) -> None:
        raise NotImplementedError()

