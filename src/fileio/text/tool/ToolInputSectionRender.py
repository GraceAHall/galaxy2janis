


from dataclasses import dataclass
from fileio.text.TextRender import TextRender
from shellparser.components.CommandComponent import CommandComponent


@dataclass
class ToolInputSectionRender(TextRender):
    entity: list[CommandComponent]

    def render(self) -> str:
        raise NotImplementedError()
        
    def collect_imports(self) -> list[str]:
        raise NotImplementedError()