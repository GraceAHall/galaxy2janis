
# pyright: strict

import xml.etree.ElementTree as et


from classes.datastructures.Params import Param
from classes.parsers.MacroParser import MacroParser
from classes.parsers.TokenParser import TokenParser
from classes.parsers.ParamParser import ParamParser
from classes.parsers.CommandParser import CommandParser
from classes.parsers.MetadataParser import MetadataParser

"""
This class mostly acts as an orchestrator.
Tool.xml is parsed in a stepwise manner, where each step has its own class to perform the step.
"""

class ToolParser:
    def __init__(self, filename: str, workdir: str):
        self.filename = filename
        self.workdir = workdir
        self.tree: et.ElementTree = et.parse(f'{workdir}/{filename}')
        self.root: et.Element = self.tree.getroot()
        self.command_lines: list[str] = [] 

        self.galaxy_depth_elems = ['conditional', 'section']
        self.ignore_elems = ['outputs', 'tests']
        self.parsable_elems = ['description', 'command', 'param', 'repeat', 'help', 'citations']

        self.tree_path: list[str] = []
        self.tokens: dict[str, str] = {}
        self.params: dict[str, Param] = {}


    # 1st step: macro expansion (preprocessing)
    def parse_macros(self) -> None:
        mp = MacroParser(self.workdir, self.filename)
        mp.parse()
        self.tree = mp.tree 
        
        # update the xml tree
        self.tokens.update(mp.tokens)
        self.root = self.tree.getroot() #type: ignore - is this necessary?
        self.check_macro_expansion(self.root)


    # 2nd step: token handling (preprocessing)
    def parse_tokens(self):
        tp = TokenParser(self.tree, self.tokens)
        tp.parse()
        self.tree = tp.tree
        print()


    # 3rd step: command parsing & linking to params
    def parse_command(self):
        cp = CommandParser(self.tree, self.params)
        self.command_lines = cp.parse()
        print()


    # 4th step: param parsing
    def parse_params(self):
        # includes repeats
        # includes outputs? 
        pp = ParamParser(self.tree, self.command_lines)
        pp.parse()
        self.params = pp.params




    # 5th step: parsing tool metadata
    def parse_metadata(self):
        mp = MetadataParser(self.tree)
        mp.parse()
        print()
    


    # ============== debugging ============== #

    def check_macro_expansion(self, node: et.Element) -> None:
        for child in node:
            assert(child.tag != 'expand')
            self.check_macro_expansion(child)


    def write_tree(self, filepath: str) -> None:
        #et.dump(self.root)
        with open(filepath, 'w') as f:
            self.tree.write(f, encoding='unicode')


    def pretty_print(self) -> None:
        for param in self.params.values():
            print(param)






