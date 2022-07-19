


from typing import Tuple

from entities.workflow import WorkflowInput

from ..TextRender import TextRender
from .. import ordering

import tags
import datatypes


class WorkflowInputText(TextRender):
    def __init__(self, entity: WorkflowInput):
        super().__init__()
        self.entity = entity

    @property
    def imports(self) -> list[Tuple[str, str]]:
        jtype = datatypes.get(self.entity)
        imports: list[Tuple[str, str]] = []
        imports.append((jtype.import_path, jtype.classname))

        # TODO opportunity for decorator
        if self.entity.array:
            imports.append(('janis_core', 'Array'))

        # TODO opportunity for decorator
        imports = list(set(imports))
        return ordering.order_imports(imports)

    def render(self) -> str:
        tag = tags.get(self.entity.uuid)
        type_str = datatypes.get_str(entity=self.entity)
        out_str: str = ''
        out_str += f'w.input("{tag}", {type_str})'
        #out_str += f'\t"{tag}",\n'
        #out_str += f'\t{datatype}'
        #out_str += f',\n\tdefault={default}' if default else ''  # TODO HERE
        #out_str += f',\n\tvalue={value}' if value else ''
        #out_str += f',\n\tdoc="{doc}"' if doc else ''
        #out_str += '\n)\n'
        return out_str