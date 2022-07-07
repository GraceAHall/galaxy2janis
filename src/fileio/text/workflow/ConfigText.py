
from typing import Tuple

from entities.workflow.workflow import Workflow
from fileio.text.TextRender import TextRender


class ConfigText(TextRender):
    def __init__(self, entity: Workflow, render_imports: bool=False):
        super().__init__(render_imports)
        self.entity = entity

    @property
    def imports(self) -> list[Tuple[str, str]]:
        raise NotImplementedError()

    def render(self) -> str:
        raise NotImplementedError()
    
