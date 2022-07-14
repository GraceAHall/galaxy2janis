

from dataclasses import dataclass
from typing import Optional, Tuple

from gx.command.components import OutputComponent
from gx.command.components import InputOutput
from gx.command.components import RedirectOutput
from gx.command.components import UncertainOutput
from gx.command.components import WildcardOutput

from ..TextRender import TextRender
from .. import formatting
from .. import ordering

from datatypes import get
import tags


def format_selector_str(output: OutputComponent) -> Optional[str]:
    match output: 
        case RedirectOutput():
            return None
        case InputOutput():
            input_comp_uuid = output.input_component.uuid
            input_comp_tag = tags.tool.get(input_comp_uuid)
            return f'InputSelector("{input_comp_tag}")'
        case WildcardOutput() | UncertainOutput():
            pattern = output.gxparam.wildcard_pattern # what
            return f'WildcardSelector("{pattern}")'
        case _:
            pass


@dataclass
class ToolOutputText(TextRender):
    def __init__(self, entity: OutputComponent):
        super().__init__()
        self.entity = entity

    @property
    def imports(self) -> list[Tuple[str, str]]:
        jtypes = get(self.entity)
        imports: list[Tuple[str, str]] = []
        imports = [(j.import_path, j.classname) for j in jtypes]

        # TODO opportunity for decorator # Stdout class import
        if isinstance(self.entity, RedirectOutput):
            imports.append(('janis_core', 'Stdout'))
        # TODO opportunity for decorator # Selector class import
        selector_str = format_selector_str(self.entity)
        if selector_str:
            selector = selector_str.split('(', 1)[0]
            imports.append(('janis_core', selector))
        # TODO opportunity for decorator # Array class import
        if self.entity.array:
            imports.append(('janis_core', 'Array'))

        # TODO opportunity for decorator
        imports = list(set(imports))
        return ordering.order_imports(imports)

    def render(self) -> str:
        e = self.entity
        selector_str = format_selector_str(e)
        doc = formatting.format_docstring(e)
        out_str: str = ''
        out_str += '\tToolOutput(\n'
        out_str += f"\t\t'{tags.tool.get(e.uuid)}',\n"
        out_str += f"\t\t{formatting.format_datatype_string(e)},\n"
        if selector_str:
            out_str += f"\t\tselector={selector_str},\n" 
        out_str += f'\t\tdoc="{doc}",\n' if doc else ''
        out_str += '\t)'
        return out_str

    