

#pyright: basic

from xml.etree import ElementTree as et
from typing import Union



from classes.logging.Logger import Logger
from utils.etree_utils import get_attribute_value


class MetadataXMLParser:
    def __init__(self, tree: et.ElementTree, logger: Logger) -> None:
        self.tree = tree
        self.logger = logger

        # tool metadata to collect:
        self.tool_name: str = ''
        self.tool_id: str = ''
        self.tool_version: str = ''
        self.description: str = ''
        self.requirements: list[dict[str, Union[str, int]]] = [] # lol typing is so bad here
        self.citations: list[dict[str, str]] = []
        self.help: str = ''


    def parse(self) -> None:
        self.set_tool_metadata()
        root = self.tree.getroot()

        # iterate through tree parsing relevant elems
        for node in root:
            self.parse_elem(node)


    def set_tool_metadata(self) -> None:
        root = self.tree.getroot()
        self.tool_name = root.attrib['name']
        self.tool_id = root.attrib['id']
        self.tool_version = root.attrib['version'].split('+galaxy')[0] or ''


    def parse_elem(self, node: et.Element) -> None:
        if node.tag == 'requirements':
            self.parse_requirements(node)
        elif node.tag == 'citations':
            self.parse_citations(node)
        elif node.tag == 'description':
            self.parse_description(node)
        elif node.tag == 'help':
            self.parse_help(node)
        
        for child in node:
            self.parse_elem(child)
    

    def parse_requirements(self, node: et.Element) -> None:
        requirements = node.findall('requirement')
        containers = node.findall('container')
        
        for requirement in requirements:
            self.parse_requirement(requirement)
        for container in containers:
            self.parse_container(container)


    def parse_requirement(self, node: et.Element) -> None:
            req_type = get_attribute_value(node, 'type')
            req_version = get_attribute_value(node, 'version')
            req_name = node.text or ''
            requirement = {'type': req_type, 'version': req_version, 'name': req_name, 'aln_score': 0}
            self.requirements.append(requirement)


    def parse_container(self, node: et.Element) -> None:
        req_name = node.text or ''
        req_type = get_attribute_value(node, 'type')
        requirement = {'type': req_type, 'version': '', 'name': req_name, 'aln_score': 0}
        self.requirements.append(requirement)


    def parse_citations(self, node: et.Element) -> None:
        citation_nodes = node.findall('citation')
        
        for cit_node in citation_nodes:
            cit_type = get_attribute_value(cit_node, 'type')
            citation = {'type': cit_type, 'text': cit_node.text or ''} 
            self.citations.append(citation)


    def parse_description(self, node: et.Element) -> None:
        self.description = node.text # type: ignore

    
    def parse_help(self, node: et.Element) -> None:
        self.help = node.text or ''
 
