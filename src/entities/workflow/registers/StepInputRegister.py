

from typing import Optional

from ..step.inputs import InputValue

import tags


class StepInputRegister:
    def __init__(self):
        self.inputs: list[InputValue] = []

    @property
    def all(self) -> list[InputValue]:
        return self.inputs
    
    @property
    def linked(self) -> list[InputValue]:
        return [x for x in self.inputs if x.component]
    
    @property
    def unlinked(self) -> list[InputValue]:
        return [x for x in self.inputs if not x.component]

    def add(self, invalue: InputValue) -> None:
        self.inputs.append(invalue)
    
    def get(self, query_uuid: str) -> Optional[InputValue]:
        for invalue in self.inputs:
            if invalue.component and invalue.component.uuid == query_uuid:
                return invalue

    def __str__(self) -> str:
        out: str = '\nInputValueRegister -----\n'
        out += f"{'[gxparam]':30}{'[input type]':30}{'[value]':30}\n"
        for inval in self.inputs:
            if inval.component:
                label = tags.tool.get(inval.component.uuid)
            else:
                label = 'unlinked'
            out += f'{label:30}{str(type(inval).__name__):30}{inval.tag_and_value:30}\n'
        return out


