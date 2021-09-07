

from xml.etree import ElementTree as et


class MetadataParser:
    def __init__(self, tree: et.ElementTree):
        self.tree = tree

        # tool metadata to collect:
        self.tool_name = ''
        self.tool_version = ''
        self.citations = ''
        self.description = ''
        self.help = ''
        self.containers = {}


    def parse(self) -> None:
        self.set_tool_metadata()

        for node in self.tree.iter():
            self.parse_elem(node)


    def set_tool_metadata(self) -> None:
        root = self.tree.getroot()
        self.tool_name = root.attrib['id']
        self.tool_version = root.attrib['version']


    def parse_elem(self, node: et.Element) -> None:
        if node.tag == 'citations':
            self.parse_citations(node)
        elif node.tag == 'description':
            self.parse_description(node)
        elif node.tag == 'container':
            self.parse_container(node)
        elif node.tag == 'help':
            self.parse_help(node)
        
        for child in node:
            self.parse_elem(child)
    

    def parse_citations(self, node):
        pass


    def parse_description(self, node):
        pass

    
    def parse_container(self, node: et.Element) -> None:
        key = node.attrib['name']
        val = node.text or ""
        self.tool.containers[key] = val


    def parse_help(self, node):
        pass