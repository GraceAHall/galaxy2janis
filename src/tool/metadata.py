



from dataclasses import dataclass

from tool.citations import Citation


@dataclass
class Metadata:
    name: str
    id: str
    version: str
    description: str
    help: str
    citations: list[Citation]
    creator: str