
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from messages import Message


class CurationState(Enum):
    RAW     = auto()
    EDITED  = auto()
    CURATED = auto()

class Confidence(Enum):
    LOW     = auto()
    MEDIUM  = auto()
    HIGH    = auto()


@dataclass
class TextRender(ABC):
    entity: Any
    messages: list[Message]
    
    def __post_init__(self):
        self.imports: list[str] = self.collect_imports() # ???
        self.curation_state: CurationState = CurationState.RAW
        self.confidence: Confidence = Confidence.LOW

    @abstractmethod
    def render(self) -> str:
        """renders an entity to text"""
        ...
    
    @abstractmethod
    def collect_imports(self) -> list[str]:
        """collects all imports this entity will need"""
        ...




