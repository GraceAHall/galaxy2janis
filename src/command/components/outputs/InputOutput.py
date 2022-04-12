

from __future__ import annotations
from command.components.CommandComponent import CommandComponent, BaseCommandComponent
from typing import Any, Optional
from xmltool.param.OutputParam import DataOutputParam, CollectionOutputParam


class InputOutput(BaseCommandComponent):
    def __init__(self, input_component: CommandComponent):
        super().__init__()
        self.input_component = input_component
        self.gxparam = self.input_component.gxparam
        assert(self.gxparam)

    def get_name(self) -> str:
        if self.gxparam:
            return self.gxparam.name
        raise RuntimeError('an InputOutput must have an input_component with an attached gxparam')

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
        return f'output created during runtime. file relates to the {self.input_component.get_tag()} input'

    def update(self, incoming: InputOutput) -> None:
        raise NotImplementedError()

    def get_selector_str(self) -> str:
        return f'InputSelector("{self.input_component.get_tag()}")'

