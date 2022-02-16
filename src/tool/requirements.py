





from abc import ABC, abstractmethod
from dataclasses import dataclass


"""
EXAMPLE
<requirements>
    <requirement type="package" version="1.2.0">bowtie</requirement>
    <container type="docker">google/deepvariant:@TOOL_VERSION@</container>
</requirements>
"""



@dataclass
class Requirement(ABC):
    @abstractmethod
    def get_text(self) -> str:
        ...

@dataclass
class CondaRequirement(Requirement):
    name: str
    version: str

    def get_text(self) -> str:
        return self.name

@dataclass
class ContainerRequirement(Requirement):
    uri: str

    def get_text(self) -> str:
        return self.uri






