


from typing import Protocol

from galaxy.tools import Tool as GxTool

from tool.tool_definition import GalaxyToolDefinition
from tool.parsing.GalaxyToolIngestor import GalaxyToolIngestor
from tool.param.InputRegister import InputRegister
from tool.param.OutputRegister import OutputRegister
from tool.test import TestRegister
from tool.requirements import Requirement
from tool.metadata import Metadata


class Ingestor(Protocol):
    def get_metadata(self) -> Metadata:
        """returns a formatted Metadata using the representation"""
        ...
    
    def get_requirements(self) -> list[Requirement]:
        """returns a formatted list of Requirements using the representation"""
        ...
    
    def get_command(self) -> str:
        """returns a formatted list of Requirements using the representation"""
        ...
    
    def get_inputs(self) -> InputRegister:
        """returns a formatted list of params using the representation"""
        ...
    
    def get_outputs(self) -> OutputRegister:
        """returns a formatted list of outputs using the representation"""
        ...
    
    def get_tests(self) -> TestRegister:
        """returns a formatted list of tests using the representation"""
        ...


def parse_gx_to_internal(gxtool: GxTool) -> GalaxyToolDefinition:
    ingestor = GalaxyToolIngestor(gxtool)
    return GalaxyToolDefinition(
        ingestor.get_metadata(),
        ingestor.get_command(),
        ingestor.get_inputs(),
        ingestor.get_outputs(),
        ingestor.get_tests()
    )

