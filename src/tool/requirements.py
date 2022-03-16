

from abc import ABC
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
    """models a tool XML requirement"""

    def get_text(self) -> str:
        ...

    def get_version(self) -> str:
        ...
    
    def get_type(self) -> str:
        ...


@dataclass
class CondaRequirement(Requirement):
    name: str
    version: str

    def get_text(self) -> str:
        return self.name

    def get_version(self) -> str:
        return self.version
    
    def get_type(self) -> str:
        return 'conda'


@dataclass
class ContainerRequirement(Requirement):
    uri: str
    container_type: str

    def get_text(self) -> str:
        return self.uri

    def get_version(self) -> str:
        raise NotImplementedError

    def get_type(self) -> str:
        return self.container_type





