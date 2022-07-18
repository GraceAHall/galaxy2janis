


from typing import Tuple

from entities.workflow.step.outputs import StepOutput

from ..TextRender import TextRender
from .. import ordering

import tags
import datatypes


class WorkflowOutputText(TextRender):
    def __init__(self, entity: StepOutput):
        super().__init__()
        self.entity = entity

    @property
    def imports(self) -> list[Tuple[str, str]]:
        jtype = datatypes.get(self.entity.tool_output)
        imports: list[Tuple[str, str]] = []
        imports.append((jtype.import_path, jtype.classname))

        # TODO opportunity for decorator
        if self.entity.tool_output.array:
            imports.append(('janis_core', 'Array'))

        # TODO opportunity for decorator
        imports = list(set(imports))
        return ordering.order_imports(imports)

    def render(self) -> str:
        tag = tags.workflow.get(self.entity.uuid)
        step_tag = tag.rsplit('.', 1)[0]
        output_tag = tag.rsplit('.', 1)[1]
        type_str = datatypes.get_str(entity=self.entity.tool_output)
        out_str: str = ''
        out_str += 'w.output(\n'
        out_str += f'\t"{tag}",\n'
        out_str += f'\t{type_str},\n'
        out_str += f'\tsource=(w.{step_tag}, "{output_tag}")'
        # out_str += f',\n\toutput_folder="{output_folder}"' if output_folder else ''
        # out_str += f',\n\toutput_name="{output_name}"' if output_name else ''
        # out_str += f',\n\textension="{extension}"' if extension else ''
        # out_str += f',\n\tdoc="{doc}"' if doc else ''
        out_str += '\n)\n'
        return out_str