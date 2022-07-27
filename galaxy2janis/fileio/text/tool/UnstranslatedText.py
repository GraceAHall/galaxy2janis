

from __future__ import annotations
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from galaxy2janis.entities.workflow import WorkflowStep

from ..TextRender import TextRender


class UntranslatedText(TextRender):
    def __init__(self, entity: WorkflowStep):
        super().__init__()
        self.entity = entity

    @property
    def imports(self) -> list[Tuple[str, str]]:
        return []

    def render(self) -> str:
        step = self.entity
        out_str: str = ''
        if step.preprocessing:
            out_str += '\n# PRE-PROCESSING ---------------------\n\n'
            out_str += step.preprocessing
        if step.postprocessing:
            out_str += '\n# POST-PROCESSING ---------------------\n\n'
            out_str += step.postprocessing
        return out_str