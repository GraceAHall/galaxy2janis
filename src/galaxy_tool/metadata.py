



from dataclasses import dataclass
from typing import Optional

from galaxy_tool.citations import Citation


@dataclass
class Metadata:
    name: str
    id: str
    version: str
    description: str
    help: str
    citations: list[Citation]
    creator: Optional[str]