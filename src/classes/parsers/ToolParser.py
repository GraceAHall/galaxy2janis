
# pyright: strict

import xml.etree.ElementTree as et
from classes.Logger import Logger


from classes.datastructures.Params import Param
from classes.datastructures.Output import Output
from classes.datastructures.Configfile import Configfile

from classes.parsers.MacroParser import MacroParser
from classes.parsers.TokenParser import TokenParser
from classes.parsers.CommandParser import CommandParser
from classes.parsers.ParamParser import ParamParser
from classes.ParamPostProcessor import ParamPostProcessor
from classes.parsers.OutputParser import OutputParser
from classes.parsers.MetadataParser import MetadataParser

"""
This class mostly acts as an orchestrator.
Tool.xml is parsed in a stepwise manner, where each step has its own class to perform the step.
"""

class ToolParser:
    def __init__(self, filename: str, workdir: str, outdir: str):
        self.filename = filename
        self.workdir = workdir
        self.outdir = outdir
        self.tree: et.ElementTree = et.parse(f'{workdir}/{filename}')
        self.root: et.Element = self.tree.getroot()

        self.galaxy_depth_elems = ['conditional', 'section']
        self.ignore_elems = ['outputs', 'tests']
        self.parsable_elems = ['description', 'command', 'param', 'repeat', 'help', 'citations']

        self.tree_path: list[str] = []
        self.tokens: dict[str, str] = {}
        self.command_lines: list[str] = [] 
        self.configfiles: list[Configfile] = []
        self.params: list[Param] = []
        self.outputs: list[Output] = []

        self.logger = Logger(self.outdir)


    def parse(self) -> None:
        self.parse_macros()
        self.parse_tokens()
        self.parse_command()
        self.parse_params()
        self.parse_outputs()
        self.parse_metadata()


    # 1st step: macro expansion (preprocessing)
    def parse_macros(self) -> None:
        mp = MacroParser(self.workdir, self.filename, self.logger)
        mp.parse()
        self.tree = mp.tree 
        
        # update the xml tree
        self.tokens.update(mp.tokens)
        self.root = self.tree.getroot() #type: ignore - is this necessary?
        self.check_macro_expansion(self.root)


    # 2nd step: token handling (preprocessing)
    def parse_tokens(self):
        tp = TokenParser(self.tree, self.tokens, self.logger)
        tp.parse()
        self.tree = tp.tree
        print()


    # 2.5th step: configfiles (preprocessing)
    def parse_configfiles(self):
        cp = ConfigfileParser(self.tree, self.tokens, self.logger)
        cp.parse()
        self.configfiles = cp.configfiles


    # 3rd step: command parsing & linking to params
    def parse_command(self):
        cp = CommandParser(self.tree)
        self.command_lines = cp.parse()


    # 4th step: param parsing
    def parse_params(self):
        # parse params
        pp = ParamParser(self.tree, self.command_lines)
        params = pp.parse()

        print('\n--- Before cleaning ---\n')
        print(f'{"name":30}{"datatype":25}{"prefix":20}{"command":>10}')
        print('-' * 75)
        for param in params:
            print(param)

        # cleanup steps
        ppp = ParamPostProcessor(params)
        ppp.remove_duplicate_params()

        print('\n--- After cleaning ---\n')
        print(f'{"name":30}{"datatype":25}{"prefix":20}{"command":>10}')
        print('-' * 75)
        for param in ppp.params:
            print(param)

        # update params to cleaned param list
        self.params = ppp.params
        print()


    # 5th step: output parsing
    def parse_outputs(self):
        op = OutputParser(self.tree, self.params, self.command_lines)
        self.outputs = op.parse()


    # 6th step: parsing tool metadata
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
        pass






