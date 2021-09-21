

#pyright: strict

from xml.etree import ElementTree as et

from classes.Logger import Logger
from utils.etree_utils import get_attribute_value


class MetadataParser:
    def __init__(self, tree: et.ElementTree, logger: Logger) -> None:
        self.tree = tree
        self.logger = logger

        # tool metadata to collect:
        self.tool_name: str = ''
        self.galaxy_version: str = ''
        self.citations: list[dict[str, str]] = []
        self.requirements: list[dict[str, str]] = []
        self.description: str = ''
        self.help: str = ''
        self.containers: dict[str, str] = {}


    def parse(self) -> None:
        self.set_tool_metadata()
        root = self.tree.getroot()

        for node in root:
            self.parse_elem(node)


    def set_tool_metadata(self) -> None:
        root = self.tree.getroot()
        self.tool_name = root.attrib['id']
        self.galaxy_version = root.attrib['version']


    def parse_elem(self, node: et.Element) -> None:
        if node.tag == 'requirements':
            self.parse_requirements(node)
        elif node.tag == 'citations':
            self.parse_citations(node)
        elif node.tag == 'description':
            self.parse_description(node)
        elif node.tag == 'container':
            self.parse_container(node)
        elif node.tag == 'help':
            self.parse_help(node)
        
        for child in node:
            self.parse_elem(child)
    

    def parse_requirements(self, node: et.Element) -> None:
        requirements = node.findall('requirement')
        
        for req_node in requirements:
            req_type = get_attribute_value(req_node, 'type')
            req_version = get_attribute_value(req_node, 'version')
            req_name = req_node.text or ''
            requirement = {'type': req_type, 'version': req_version, 'name': req_name}
            self.requirements.append(requirement)


    def parse_citations(self, node: et.Element) -> None:
        citation_nodes = node.findall('citation')
        
        for cit_node in citation_nodes:
            cit_type = get_attribute_value(cit_node, 'type')
            citation = {'type': cit_type, 'text': cit_node.text or ''} 
            self.citations.append(citation)


    def parse_description(self, node: et.Element) -> None:
        self.description = node.text # type: ignore

    
    def parse_container(self, node: et.Element) -> None:
        key = node.attrib['name']
        val = node.text or ""
        self.containers[key] = val


    def parse_help(self, node: et.Element) -> None:
        self.help = node.text or ''