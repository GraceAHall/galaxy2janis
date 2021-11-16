
# pyright: basic

import xml.etree.ElementTree as et
from classes.Logger import Logger
from typing import Union
import sys
from classes.outputs.OutputRegister import OutputRegister
from classes.params.ParamRegister import ParamRegister

from classes.command.Command import Command
from classes.command.CommandProcessor import CommandProcessor
from classes.command.Configfile import Configfile

from classes.containers.ContainerFetcher import ContainerFetcher

from classes.parsers.MacroParser import MacroParser
from classes.parsers.TokenParser import TokenParser
from classes.parsers.ConfigfileParser import ConfigfileParser
from classes.parsers.CommandParser import CommandParser
from classes.parsers.ParamParser import ParamParser
from classes.janis.DatatypeAnnotator import DatatypeAnnotator
from classes.janis.JanisFormatter import JanisFormatter
from classes.parsers.OutputParser import OutputParser
from classes.parsers.MetadataParser import MetadataParser

"""
This class mostly acts as an orchestrator.
Tool.xml is parsed in a stepwise manner, where each step has its own class to perform the step.
"""


#pyright: strict

from typing import Optional

#from classes.datastructures import Param

 
class Tool:
    def __init__(self):
        self.name: str = ""
        self.id: str = ""
        self.version: str = ""
        self.creator: Optional[str] = None
        self.main_requirement: Optional[dict[str, Union[str, int]]] = None
        self.container: Optional[dict[str, str]] = None
        self.tests: Optional[str] = None
        self.help: str = ""
        self.citations: list[dict[str, str]] = []
        self.tool_module: str = 'bioinformatics' 
        self.command: Optional[Command] = None  
        self.param_register: Optional[ParamRegister] = None
        self.out_register: Optional[OutputRegister] = None



class ToolParser:
    def __init__(self, tool_xml: str, tool_workdir: str, out_log: str, out_def: str, debug: bool=False):
        self.filename = tool_xml
        self.workdir = tool_workdir
        self.debug = debug
        self.logfile = out_log
        self.janis_out_path = out_def
        self.tree: et.ElementTree = et.parse(f'{self.workdir}/{self.filename}')
        self.root: et.Element = self.tree.getroot()

        self.galaxy_depth_elems = ['conditional', 'section']
        self.ignore_elems = ['outputs', 'tests']
        self.parsable_elems = ['description', 'command', 'param', 'repeat', 'help', 'citations']

        # tool metadata
        self.tool_name: str = ''
        self.tool_id: str = ''
        self.tool_version: str = ''
        self.tool_creator: str = ''
        self.citations: list[dict[str, str]] = []
        self.requirements: list[dict[str, Union[str, int]]] = []
        self.main_requirement: Optional[dict[str, Union[str, int]]] = None
        self.container: Optional[dict[str, str]] = None
        self.description: str = ''
        self.help: str = ''

        # param and output parsing
        self.tree_path: list[str] = []
        self.tokens: dict[str, str] = {}
        self.command_lines: list[str] = [] 
        self.configfiles: list[Configfile] = []
        self.command: Command = Command() 
        self.param_register: ParamRegister = ParamRegister()  
        self.out_register: OutputRegister = OutputRegister() 

        self.logger = Logger(self.logfile)
        self.tool = None


    def parse(self) -> None:
        """
        May be a need for a postprocessing step after annotate_datatypes
        to do stuff like confirm the base command etc
        """
        # basic setup
        self.parse_macros()
        self.parse_tokens()
        self.parse_metadata()
        self.fetch_container()

        # gathering UI variables
        self.parse_params()
        self.parse_outputs()
        self.parse_configfiles()
        
        # the business
        self.parse_command()
        self.annotate_datatypes()
        self.init_tool()
        self.write_janis()
        sys.exit()
        #self.postprocess()


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
        self.tool_version = mp.tool_version
        self.description = mp.description
        self.requirements = mp.requirements
        self.citations = mp.citations
        self.help = mp.help


    def fetch_container(self):
        cf = ContainerFetcher(self.tool_id, self.tool_version, self.requirements, self.logger)
        cf.fetch()

        self.main_requirement = cf.main_requirement # type: ignore
        self.container = cf.container # type: ignore


    # 4th step: param parsing
    def parse_params(self):
        pp = ParamParser(self.tree, self.logger)
        params = pp.parse()
        if self.debug:
            pp.pretty_print()
        self.param_register.add(params)


    # 5th step: output parsing
    def parse_outputs(self):
        op = OutputParser(self.tree, self.param_register, self.logger)
        outputs = op.parse() 
        if self.debug:
            op.pretty_print()
        self.out_register.add(outputs)


    # 6th step: configfile parsing
    def parse_configfiles(self):
        cp = ConfigfileParser(self.tree, self.tokens, self.logger)
        cp.parse()
        self.configfiles = cp.configfiles


    # 7th step: command parsing 
    def parse_command(self):
        # parse command text into useful representation
        cpar = CommandParser(self.tree, self.logger)
        cpar.parse()
        if self.debug:
            cpar.pretty_print_command_words()
        
        # create Command() object
        cpro = CommandProcessor(cpar.lines, cpar.command_words, self.param_register, self.out_register, self.logger) # type: ignore
        command = cpro.process()
        cpro.pretty_print_tokens()
        self.command = command


    # 8th step: annotating with datatypes
    def annotate_datatypes(self):
        da = DatatypeAnnotator(self.command, self.param_register, self.out_register, self.logger)
        da.annotate()
        if self.debug:
            self.command.pretty_print()


    def init_tool(self):
        """
        this just creates a clean format for conversion to janis
        mostly for my own mental clutter
        """
        tool = Tool()
        tool.name = self.tool_name
        tool.id = self.tool_id
        tool.version = self.tool_version
        tool.creator = None  # TODO this is just temp
        tool.container = self.container
        tool.tests = None  # TODO this is just temp
        tool.help = self.help
        tool.citations = self.citations
        tool.command = self.command
        tool.param_register = self.param_register
        tool.out_register = self.out_register
        self.tool = tool  
        

    # 9th step: convert to janis definition & write
    def write_janis(self):
        # generate janis py
        jf = JanisFormatter(self.tool, self.janis_out_path, self.logger) # type: ignore
        jf.format()
        jf.write()





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






