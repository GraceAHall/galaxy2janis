


from typing import Protocol, Tuple

from dataclasses import dataclass
from galaxy.tools import Tool as GalaxyTool

from classes.xml.GalaxyXMLParser import GalaxyXMLParser
from classes.xml.LocalXMLParser import LocalXMLParser
from classes.tool.Ingestion import (
    IngestStrategy, 
    GalaxyIngestStrategy, 
    LocalIngestStrategy
)



class XMLParser(Protocol):
    def parse(self, xml_path: str) -> GalaxyTool:
        """reads xml files and returns a tool representation"""
        ...


@dataclass
class GalaxyToolDefinition:
    def __init__(self, xml_path: str, parser: str='galaxy'):
        loader, formatter = self.get_parsing_objects(parser)
        representation = loader.parse(xml_path)
        self.metadata = formatter.get_metadata(representation)
        self.requirements = formatter.get_requirements(representation)
        self.params = formatter.get_params(representation)
        self.outputs = formatter.get_outputs(representation)
        self.tests = formatter.get_tests(representation)


    def get_parsing_objects(self, parser: str) -> Tuple[XMLParser, IngestStrategy]:
        match parser:
            case 'galaxy':
                return GalaxyXMLParser(), GalaxyIngestStrategy()
            case 'local':
                return LocalXMLParser(), LocalIngestStrategy()
            case _:
                return GalaxyXMLParser(), GalaxyIngestStrategy()


















    # def update_metadata(self, meta: Metadata) -> None:
    #     self.transfer_attributes(meta)
    #     self.version = self.version.rsplit('+galaxy', 1)[0]

    # def transfer_attributes(self, meta: Metadata) -> None:
    #     for k, v in meta.__dict__.items():
    #         self.__dict__[k] = v

    # def get_help(self) -> str:
    #     return repr(self.help)