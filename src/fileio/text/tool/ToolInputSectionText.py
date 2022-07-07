


from dataclasses import dataclass
from typing import Tuple
from fileio.text.TextRender import TextRender
from fileio.text.tool.ToolInputText import ToolInputText

from shellparser.components.inputs.InputComponent import InputComponent

from shellparser.components.inputs.Flag import Flag
from shellparser.components.inputs.Option import Option
from shellparser.components.inputs.Positional import Positional

from .. import ordering
from .. import formatting

@dataclass
class ToolInputSectionText(TextRender):
    def __init__(self, entity: list[InputComponent], render_imports: bool=False):
        super().__init__(render_imports)
        self.entity = entity

    @property
    def imports(self) -> list[Tuple[str, str]]:
        imports: list[Tuple[str, str]] = []
        for inp in self.entity:
            imports += ToolInputText(inp).imports
        imports = list(set(imports))
        return ordering.order_imports(imports)

    def render(self) -> str:
        out_str: str = ''

        if self.render_imports:
            out_str += f'{formatting.format_imports(self.imports)}\n'

        out_str += 'inputs = ['

        out_str += '\n\t# Positionals\n'
        for positional in self._get_positionals():
            render = ToolInputText(positional)
            out_str += f'{render.render()},\n'

        out_str += '\n\t# Flags\n'
        for flag in self._get_flags():
            render = ToolInputText(flag)
            out_str += f'{render.render()},\n'

        out_str += '\n\t# Options\n'
        for option in self._get_options():
            render = ToolInputText(option)
            out_str += f'{render.render()},\n'
        
        out_str += '\n]\n'
        return out_str

    def _get_positionals(self) -> list[Positional]:
        positionals = [x for x in self.entity if isinstance(x, Positional)]
        return ordering.order_positionals(positionals)
    
    def _get_flags(self) -> list[Flag]:
        flags = [x for x in self.entity if isinstance(x, Flag)]
        return ordering.order_flags(flags)
    
    def _get_options(self) -> list[Option]:
        options = [x for x in self.entity if isinstance(x, Option)]
        return ordering.order_options(options)

    