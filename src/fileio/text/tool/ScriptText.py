

from typing import Tuple

from entities.workflow import Workflow
from ..TextRender import TextRender


class ScriptText(TextRender):
    def __init__(self, entity: Workflow, render_imports: bool=False):
        super().__init__()
        self.entity = entity
        self.render_imports = render_imports

    @property
    def imports(self) -> list[Tuple[str, str]]:
        raise NotImplementedError()

    def render(self) -> str:
        raise NotImplementedError()
    
