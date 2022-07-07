


from dataclasses import dataclass
from typing import Tuple
from fileio.text.TextRender import TextRender
from fileio.text.tool.ToolOutputText import ToolOutputText
from shellparser.components.outputs.OutputComponent import OutputComponent

from .. import ordering
from .. import formatting

@dataclass
class ToolOutputSectionText(TextRender):
    def __init__(self, entity: list[OutputComponent], render_imports: bool=False):
        super().__init__(render_imports)
        self.entity = entity
    
    @property
    def imports(self) -> list[Tuple[str, str]]:
        imports: list[Tuple[str, str]] = []
        for out in self.entity:
            imports += ToolOutputText(out).imports
        imports = list(set(imports))
        return ordering.order_imports(imports)

    def render(self) -> str:
        out_str: str = ''
        
        if self.render_imports:
            out_str += f'{formatting.format_imports(self.imports)}\n'

        out_str += 'outputs = [\n'
        for out in self.entity:
            render = ToolOutputText(out)
            out_str += f'\t{render.render()},\n'
        out_str += '\n]\n'

        return out_str