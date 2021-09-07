
# pyright: strict

import xml.etree.ElementTree as et


from classes.datastructures.Tool import Tool
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

        self.galaxy_depth_elems = ['conditional', 'section']
        self.ignore_elems = ['outputs', 'tests']
        self.parsable_elems = ['description', 'command', 'param', 'repeat', 'help', 'citations']

        self.tree_path: list[str] = []
        self.tokens: dict[str, str] = {}
        self.tool: Tool = Tool()


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


    # 3rd step: param parsing
    def parse_params(self):
        # includes repeats
        # includes outputs? 
        pp = ParamParser(self.tree)
        pp.parse()
        self.tree = pp.tree
        print()


    # 4th step: command parsing & linking to params
    def parse_command(self):
        cp = CommandParser(self.tree)
        cp.parse()
        self.tree = cp.tree
        print()


    # 5th step: parsing tool metadata
    def parse_metadata(self):
        mp = MetadataParser(self.tree)
        mp.parse()
        self.tree = mp.tree
        print()
    


    # ============== debugging ============== #

    def check_macro_expansion(self, node: et.Element) -> None:
        for child in node:
            assert(child.tag != 'expand')
            self.check_macro_expansion(child)


    def write_tree(self, filepath: str) -> None:
        et.dump(self.root)
        with open(filepath, 'w') as f:
            self.tree.write(f, encoding='unicode')


    def pretty_print(self) -> str:
        print(f'\n===== {classname} =====')
        print(f'name: {entity.name}')

        if hasattr(entity, 'version') and entity.version != None:
            print(f'version: {entity.version}')
        
        if hasattr(entity, 'creator') and entity.creator != None:
            print(f'creator: {entity.creator}')
        
        if hasattr(entity, 'help') and entity.help != None:
            print(f'help: {entity.help}')
        
        if hasattr(entity, 'citations') and entity.citations != None:
            print(f'citations: {entity.citations}')

        if hasattr(entity, 'tokens') and len(entity.tokens) != 0:
            print('\ntokens --------')
            for key, val in entity.tokens.items():
                print(f'{key}: {val}')

        if hasattr(entity, 'params') and len(entity.params) != 0:
            print('\nparams --------')
            for param in entity.params:
                param.print()

        if hasattr(entity, 'containers') and len(entity.containers) != 0: 
            print('\ncontainers --------')
            for container in entity.containers:
                container.print()
        
        if hasattr(entity, 'expands') and len(entity.expands) != 0: 
            print('\nexpands --------')
            for expand in entity.expands:
                print(f'macro name: {expand.macro_reference}')
                print(f'local path: {expand.local_path}')






