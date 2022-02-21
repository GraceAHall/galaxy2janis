

from dataclasses import dataclass


"""
EXAMPLE
<requirements>
    <requirement type="package" version="1.2.0">bowtie</requirement>
    <container type="docker">google/deepvariant:@TOOL_VERSION@</container>
</requirements>
"""



@dataclass
class CondaRequirement:
    name: str
    version: str

    def get_text(self) -> str:
        return self.name

    def get_version(self) -> str:
        return self.version


@dataclass
class ContainerRequirement:
    uri: str

    def get_text(self) -> str:
        return self.uri

    def get_version(self) -> str:
        raise NotImplementedError






