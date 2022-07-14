

from typing import Tuple
from gx.configfiles.Configfile import Configfile

from ..TextRender import TextRender


class ScriptText(TextRender):
    def __init__(self, entity: Configfile):
        super().__init__()
        self.entity = entity

    @property
    def imports(self) -> list[Tuple[str, str]]:
        return []

    def render(self) -> str:
        return self.entity.contents
    
