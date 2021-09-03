

from classes.parsers.SubtreeParser import SubtreeParser
from classes.datastructures.Macro import Macro
import xml.etree.ElementTree as et

# parse a single <macro> or <xml> element
class MacroParser(SubtreeParser):
    def __init__(self, filename: str, workdir: str, root: et.Element):
        super().__init__(filename, workdir, root)

        self.parsable_elems = ['token', 'description', 'expand', 'param', 'repeat', 'help', 'citations', 'container']
        self.subtree_elems = []  # macros can't have macro definitions inside. Can reference other macros. 
        self.macro = Macro(self.root.attrib['name'])
        self.set_tag_tokens()


    def print(self):
        self.print_details('Macro', self.macro)


    def set_tag_tokens(self):
        for key, val in self.root.attrib.items():
            if key.startswith('token_'):
                token_name = '@' + key.lstrip('token_').upper() + '@'
                token_value = val
                self.tokens[token_name] = token_value


    def parse_container(self, node):
        container_type = self.get_attribute_value('type')
        container_image = node.text
        self.datastructure.add_container(container_type, container_image)


    def add_param(self, param):
        self.macro.params.append(param)
  

    def add_container(self, container):
        self.macro.containers.append(container)


    def add_token(self, key, val):
        self.macro.tokens[key] = val