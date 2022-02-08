





from abc import ABC
from dataclasses import dataclass


"""
<requirements>
    <requirement type="package" version="1.2.0">bowtie</requirement>
    <container type="docker">google/deepvariant:@TOOL_VERSION@</container>
</requirements>
"""



@dataclass
class Requirement(ABC):
    pass

@dataclass
class CondaRequirement(Requirement):
    name: str
    version: str

@dataclass
class ContainerRequirement(Requirement):
    uri: str







