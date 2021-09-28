

#pyright: strict

from xml.etree import ElementTree as et
from typing import Union
from Bio import pairwise2

from classes.Logger import Logger
from utils.etree_utils import get_attribute_value


class MetadataParser:
    def __init__(self, tree: et.ElementTree, logger: Logger) -> None:
        self.tree = tree
        self.logger = logger

        # tool metadata to collect:
        self.tool_name: str = ''
        self.tool_id: str = ''
        self.galaxy_version: str = ''
        self.citations: list[dict[str, str]] = []
        self.requirements: list[dict[str, Union[str, int]]] = [] # lol typing is so bad here
        self.description: str = ''
        self.help: str = ''
        self.base_command: str = '' 
        self.container: str = ''
        self.tool_version: str = ''


    def parse(self) -> None:
        self.set_tool_metadata()
        root = self.tree.getroot()

        # iterate through tree parsing relevant elems
        for node in root:
            self.parse_elem(node)

        # tasks to do after info has been scraped
        self.align_requirements_to_toolname()
        self.base_command = str(self.requirements[0]['name'])
        self.set_container()
        self.set_tool_version()


    def set_tool_metadata(self) -> None:
        root = self.tree.getroot()
        self.tool_name = root.attrib['name']
        self.tool_id = root.attrib['id']
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
            requirement = {'type': req_type, 'version': req_version, 'name': req_name, 'aln_score': 0}
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
        req_name = node.text or ''
        requirement = {'type': 'container', 'version': '', 'name': req_name, 'aln_score': 0}
        self.requirements.append(requirement)
        

    def parse_help(self, node: et.Element) -> None:
        self.help = node.text or ''


    def align_requirements_to_toolname(self) -> None:
        """
        Align each requirement to the tool id to find the base command
        """
        for req in self.requirements:
            req['aln_score'] = self.align(self.tool_name, req['name']) # type: ignore

        self.requirements.sort(key=lambda x: x['aln_score'], reverse=True)


    def align(self, pattern: str, template: str) -> int:
        pattern = pattern.lower()
        template = template.lower()
        outcome = pairwise2.align.globalms(pattern, template, 2, -1, -.5, -.1) # type: ignore
        if len(outcome) > 0: # type: ignore
            score = outcome[0].score # type: ignore
        else:
            score = 0
        return score # type: ignore
 

    def set_container(self) -> None:
        """
        requirements have been sorted by alignment match to tool id
        the main tool requirement should be 1st in self.requirements

        (subject to change) to set the container:
            if package, use requirement name to find biocontainer
            if container, use the requirement name directly
        """
        tool_req = self.requirements[0]
        if tool_req['type'] == 'package':
            self.container = f'quay.io/biocontainers/{tool_req["name"]}'
        elif tool_req['type'] == 'container':
            self.logger.log(1, 'container requirement encountered')
            self.container = tool_req['name']
        elif tool_req['type'] == 'set_environment':
            self.logger.log(2, 'chosen base command is set_environment')


    def set_tool_version(self) -> None:
        self.tool_version = str(self.requirements[0]['version'])