
from classes.parsers.SubtreeParser import SubtreeParser
from classes.parsers.MacrosParser import MacrosParser
from classes.datastructures.Tool import Tool
import xml.etree.ElementTree as et


class ToolParser(SubtreeParser):
    def __init__(self, filename: str, workdir: str, root: et.Element):
        super().__init__(filename, workdir, root)
        self.parsable_elems = ['token', 'description', 'expand', 'command', 'param', 'repeat', 'help', 'citations']
        self.subtree_elems = ['macros']
        self.tool = Tool()
        self.set_tool_metadata()


    def set_tool_metadata(self) -> None:
        self.tool.name = self.root.attrib['id']
        self.tool.version = self.root.attrib['version']


    def print(self):
        self.print_details('Tool', self.tool)


    def parse_command(self):
        pass


    def parse_subtree(self, node, tree_path):
        # create new Parser to parse subtree. 
        # override.
        mp = MacrosParser(self.filename, self.workdir, node)
        mp.parse()
        self.tool.macros += mp.macrolist.macros


    def add_param(self, param):
        self.tool.params.append(param)
  

    def add_container(self, container):
        self.tool.containers.append(container)