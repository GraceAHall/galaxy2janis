


from galaxy_interaction import GalaxyManager
from xmltool.tool_definition import XMLToolDefinition

from typing import Protocol

from xmltool.tool_definition import XMLToolDefinition
from xmltool.parsing.GalaxyToolIngestor import GalaxyToolIngestor
from xmltool.param.InputRegister import InputRegister
from xmltool.param.OutputRegister import OutputRegister
from xmltool.TestRegister import TestRegister
from xmltool.metadata import ToolXMLMetadata
from xmltool.requirements import ContainerRequirement, CondaRequirement
Requirement = ContainerRequirement | CondaRequirement



class Ingestor(Protocol):
    def get_metadata(self) -> ToolXMLMetadata:
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


def load_xmltool(gxmanager: GalaxyManager) -> XMLToolDefinition:
    galaxytool = gxmanager.get_tool()
    ingestor = GalaxyToolIngestor(galaxytool, gxmanager.esettings)
    return XMLToolDefinition(
        ingestor.get_metadata(),
        ingestor.get_command(),
        ingestor.get_inputs(),
        ingestor.get_outputs(),
        ingestor.get_tests()
    )
