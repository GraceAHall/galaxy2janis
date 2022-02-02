


from typing import Protocol

from xml_ingestion.galaxy.GalaxyIngestor import GalaxyIngestor
from xml_ingestion.local.LocalIngestor import LocalIngestor

from tool.param import InputRegister, OutputRegister
from tool.test import TestRegister
from tool.requirements import Requirement
from tool.metadata import Metadata
from tool.tool_definition import GalaxyToolDefinition


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


def ingest(xml_path: str, method: str='galaxy'):
    ingestor = init_ingestor(xml_path, method)
    return GalaxyToolDefinition(
        ingestor.get_metadata(),
        ingestor.get_requirements(),
        ingestor.get_command(),
        ingestor.get_inputs(),
        ingestor.get_outputs(),
        ingestor.get_tests()
    )


def init_ingestor(xml_path: str, method: str='galaxy') -> Ingestor:
    ingestors = {
        'galaxy': GalaxyIngestor,
        'local': LocalIngestor
    }
    return ingestors[method](xml_path)