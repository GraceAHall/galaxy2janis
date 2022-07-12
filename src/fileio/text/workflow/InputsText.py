
from typing import Tuple

from entities.workflow import Workflow
from ..TextRender import TextRender


class InputsText(TextRender):
    def __init__(self, entity: Workflow, file_format: str='yaml'):
        super().__init__()
        self.entity = entity
        self.file_format = file_format

    @property
    def imports(self) -> list[Tuple[str, str]]:
        raise NotImplementedError()

    def render(self) -> str:
        input_list = RuntimeInputList(workflow)
        if self.file_format == 'yaml':
            return to_yaml(input_list)
        elif self.file_format == 'dict':
            return to_dict(input_list)
        else:
            raise RuntimeError('wrong format')


YAML_NONE = 'null'
INFO_TEXT = """
# This file contains workflow inputs which need to be provided by the user.
# Organised as follows: 
#     1. input data for the workflow
#     2. runtime values for each step
"""

def to_yaml(input_list: RuntimeInputList) -> str:
    out: str = ''
    out += f'{INFO_TEXT}\n'
    for section, inputs in input_list.formatted:
        out += f'# {section}\n'
        for name in inputs:
            out += f'{name}: {YAML_NONE}\n'
        out += '\n'
    return out

def to_dict(input_list: RuntimeInputList) -> str:
    raise NotImplementedError()


