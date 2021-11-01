
# pyright: strict

import xml.etree.ElementTree as et
from classes.Logger import Logger
from typing import Union

from classes.datastructures.Params import Param
from classes.datastructures.Outputs import Output
from classes.datastructures.Command import CommandString
from classes.datastructures.Configfile import Configfile

from classes.parsers.MacroParser import MacroParser
from classes.parsers.TokenParser import TokenParser
from classes.parsers.ConfigfileParser import ConfigfileParser
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
    def __init__(self, tool_xml: str, tool_workdir: str, out_log: str):
        self.filename = tool_xml
        self.workdir = tool_workdir
        self.logfile = out_log
        self.tree: et.ElementTree = et.parse(f'{self.workdir}/{self.filename}')
        self.root: et.Element = self.tree.getroot()

        self.galaxy_depth_elems = ['conditional', 'section']
        self.ignore_elems = ['outputs', 'tests']
        self.parsable_elems = ['description', 'command', 'param', 'repeat', 'help', 'citations']

        # param and output parsing
        self.tree_path: list[str] = []
        self.tokens: dict[str, str] = {}
        self.command_lines: list[str] = [] 
        self.configfiles: list[Configfile] = []
        self.params: list[Param] = []
        self.outputs: list[Output] = []

        # tool metadata
        self.tool_name: str = ''
        self.tool_id: str = ''
        self.galaxy_version: str = ''
        self.citations: list[dict[str, str]] = []
        self.requirements: list[dict[str, Union[str, int]]] = []
        self.description: str = ''
        self.help: str = ''

        self.logger = Logger(self.logfile)


    def parse(self) -> None:
        # basic setup
        self.parse_macros()
        self.parse_tokens()
        self.parse_metadata()

        # gathering UI variables
        self.parse_params()
        self.parse_outputs()
        
        # the business
        #self.parse_configfiles()
        self.parse_command()
        
        #self.link_params_to_command()


    # 1st step: macro expansion (preprocessing)
    def parse_macros(self) -> None:
        mp = MacroParser(self.workdir, self.filename, self.logger)
        mp.parse()
        self.tree = mp.tree 
        
        # update the xml tree
        self.tokens.update(mp.tokens)
        self.root = self.tree.getroot()
        self.check_macro_expansion(self.root)


    # 2nd step: token handling (preprocessing)
    def parse_tokens(self):
        tp = TokenParser(self.tree, self.tokens, self.logger)
        tp.parse()
        self.tree = tp.tree


    # 3rd step: parsing tool metadata
    def parse_metadata(self):
        mp = MetadataParser(self.tree, self.logger)
        mp.parse()
        self.tool_name = mp.tool_name
        self.tool_id = mp.tool_id
        self.galaxy_version = mp.galaxy_version
        self.citations = mp.citations
        self.requirements = mp.requirements
        self.description = mp.description
        self.help = mp.help
        self.base_command = mp.base_command
        self.container = mp.container
        self.tool_version = mp.tool_version


    # 4th step: param parsing
    def parse_params(self):
        # parse params
        pp = ParamParser(self.tree, self.command_lines, self.logger)
        params = pp.parse()

        pp.pretty_print()

        self.params = params


    # 5th step: output parsing
    def parse_outputs(self):
        op = OutputParser(self.tree, self.params, self.command_lines, self.logger)
        self.outputs = op.parse()

        op.pretty_print()


    # 6th step: configfile parsing
    def parse_configfiles(self):
        cp = ConfigfileParser(self.tree, self.tokens, self.logger)
        cp.parse()
        self.configfiles = cp.configfiles


    # 7th step: command parsing 
    def parse_command(self):
        # parse command text into useful representation
        cp = CommandParser(self.tree, self.logger)
        lines, commands = cp.parse()
        
        # create Command() object
        cmd = CommandString(lines, commands, self.params, self.outputs) # type: ignore
        cmd.process()
        self.command = cmd


    # 8th step: input and output postprocessing
    
    def link_params_to_command(self):
        """
        cleanup steps
        handles a lot of stuff
        finalises the set of options (some gx params get split)
        sets default values
        sets optionality on params
        sets datatypes
        """

        # self.command?
        ppp = ParamPostProcessor(self.params, self.logger)
        ppp.remove_duplicate_params()
        ppp.set_prefixes()

        print('\n--- After cleaning ---\n')
        ppp.pretty_print()

        # update params to cleaned param list
        self.params = ppp.params





    
    


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






