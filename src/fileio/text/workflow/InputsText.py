
from typing import Any, Tuple

from entities.workflow import Workflow
from ..TextRender import TextRender


def note_snippet(commenter: str) -> str:
    return f"""{commenter} This file contains workflow inputs which need to be provided by the user.
{commenter} Organised as follows: 
{commenter}     1. input data for the workflow
{commenter}     2. runtime values for each step
"""

class InputsText(TextRender):
    def __init__(self, entity: Workflow, file_format: str='yaml'):
        super().__init__()
        self.entity = entity
        self.file_format = file_format

    @property
    def imports(self) -> list[Tuple[str, str]]:
        raise NotImplementedError()

    def render(self) -> str:
        input_list: list[Tuple[str, Any]] = []
        for w_inp in self.entity.inputs:
            value = w_inp.value
            input_list.append((w_inp.tag, value))

        if self.file_format == 'yaml':
            return to_yaml(input_list)
        else:
            raise RuntimeError('wrong format')



YAML_NONE = 'null'
YAML_COMMENTER = '#'

def to_yaml(input_list: list[Tuple[str, Any]]) -> str:
    out_str: str = ''
    out_str += '\n'
    out_str += f'{note_snippet(commenter=YAML_COMMENTER)}'
    out_str += '\n'

    for name, value in input_list:
        if value is None:
            value = YAML_NONE
        out_str += f'{name}: {value}\n'

    return out_str


# future formats here
