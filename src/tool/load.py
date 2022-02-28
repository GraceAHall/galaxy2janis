


from galaxy_interaction import GalaxyManager
from tool.tool_definition import GalaxyToolDefinition

from typing import Protocol

from tool.tool_definition import GalaxyToolDefinition
from tool.parsing.GalaxyToolIngestor import GalaxyToolIngestor
from tool.param.InputRegister import InputRegister
from tool.param.OutputRegister import OutputRegister
from tool.TestRegister import TestRegister
from tool.metadata import Metadata
from tool.requirements import ContainerRequirement, CondaRequirement
Requirement = ContainerRequirement | CondaRequirement



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


def load_tool(gxmanager: GalaxyManager) -> GalaxyToolDefinition:
    galaxytool = gxmanager.get_tool()
    ingestor = GalaxyToolIngestor(galaxytool, gxmanager.esettings)
    return GalaxyToolDefinition(
        ingestor.get_metadata(),
        ingestor.get_command(),
        ingestor.get_inputs(),
        ingestor.get_outputs(),
        ingestor.get_tests()
    )
