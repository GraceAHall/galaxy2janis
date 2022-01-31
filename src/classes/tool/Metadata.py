



from dataclasses import dataclass
from typing import Optional

from classes.tool.Citation import Citation


@dataclass
class Metadata:
    name: str
    id: str
    version: str
    help: str
    command: str
    citations: list[Citation]
    creator: Optional[str] = None