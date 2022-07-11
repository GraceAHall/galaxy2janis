

from typing import Optional, Tuple
from gx.gxworkflow.values.values import InputValue
from shellparser.components.inputs.InputComponent import InputComponent

import tags


class StepInputRegister:
    def __init__(self):
        # TODO this will change. Need to account for subworkflows. 
        # inputs_params could be list[InputComponent] when step is toolstep
        # inputs_params could be list[WorkflowInput] in step is subworkflow
        self.linked: list[Tuple[InputComponent, InputValue]] = []
        self.unlinked: list[InputValue] = []

    def add(self, component: Optional[InputComponent], invalue: InputValue) -> None:
        if component:
            self.linked.append((component, invalue))
        else:
            self.unlinked.append(invalue)
    
    def get(self, query_uuid: str) -> Optional[InputValue]:
        for component, value in self.linked:
            if component.uuid == query_uuid:
                return value

    def __str__(self) -> str:
        out: str = '\nInputValueRegister -----\n'
        out += f"{'[gxparam]':30}{'[input type]':30}{'[value]':30}\n"
        for comp, inval in self.linked:
            component_tag = tags.tool.get(comp.uuid)
            out += f'{component_tag:30}{str(type(inval).__name__):30}{inval.abstract_value:30}\n'
        return out


