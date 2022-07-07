


from typing import Tuple

from entities.workflow.input import WorkflowInput
from fileio.text.TextRender import TextRender

import tags
import formatting
import datatypes
import ordering

class WorkflowInputText(TextRender):
    def __init__(self, entity: WorkflowInput):
        super().__init__()
        self.entity = entity

    @property
    def imports(self) -> list[Tuple[str, str]]:
        jtypes = datatypes.get(self.entity)
        imports: list[Tuple[str, str]] = []
        imports = [(j.import_path, j.classname) for j in jtypes]

        # TODO opportunity for decorator
        if self.entity.array:
            imports.append(('janis_core', 'Array'))

        # TODO opportunity for decorator
        imports = list(set(imports))
        return ordering.order_imports(imports)

    def render(self) -> str:
        tag = tags.tool.get(self.entity.uuid)
        datatype = formatting.format_datatype_string(self.entity)
        out_str: str = ''
        out_str += f'w.input("{tag}", {datatype})\n'
        #out_str += f'\t"{tag}",\n'
        #out_str += f'\t{datatype}'
        #out_str += f',\n\tdefault={default}' if default else ''  # TODO HERE
        #out_str += f',\n\tvalue={value}' if value else ''
        #out_str += f',\n\tdoc="{doc}"' if doc else ''
        #out_str += '\n)\n'
        return out_str