
# pyright: basic

#import xml.etree.ElementTree as et

from typing import Union
import sys
from classes.templating.MockClasses import MockApp
from classes.tool.Tool import Tool
from galaxy.tools import Tool as GalaxyTool

# from classes.tool.MacroXMLParser import MacroXMLParser
# from classes.tool.TokenXMLParser import TokenXMLParser

from classes.metadata.Metadata import Metadata
from classes.metadata.ContainerFetcher import ContainerFetcher

#from classes.outputs.OutputXMLParser import OutputXMLParser
from classes.outputs.OutputRegister import OutputRegister

#from classes.params.ParamXMLParser import ParamXMLParser
from classes.params.ParamRegister import ParamRegister

from classes.configfiles.Configfile import Configfile
from classes.configfiles.ConfigfileXMLParser import ConfigfileXMLParser

from classes.command.CommandString import CommandString
from classes.command.CommandParser import CommandParser
from classes.command.Command import Command

from classes.janis.DatatypeAnnotator import DatatypeAnnotator
from classes.janis.JanisFormatter import JanisFormatter

from classes.logging.Logger import Logger
from classes.tool.GalaxyLoader import GalaxyLoader


"""
This class mostly acts as an orchestrator.
Tool.xml is parsed in a stepwise manner, where each step has its own class to perform the step.
"""


from typing import Optional

#from classes.datastructures import Param

 

        

class ToolParser:
    def __init__(self, tool_xml: str, tool_workdir: str, out_log: str, out_def: str, debug: bool=False):
        self.filename = tool_xml
        self.workdir = tool_workdir
        self.janis_out_path = out_def
        self.debug = debug
        
        self.gx_loader: GalaxyLoader = GalaxyLoader(self.workdir, self.filename)
        self.app: MockApp = self.gx_loader.init_app()
        self.gxtool: GalaxyTool = self.gx_loader.init_tool(self.app)
        self.tool: Tool = Tool()
        
        self.logfile = out_log
        self.logger = Logger(self.logfile)
        
        # self.tree: et.ElementTree = et.parse(f'{self.workdir}/{self.filename}')
        # self.root: et.Element = self.tree.getroot()
        # self.galaxy_depth_elems = ['conditional', 'section']
        # self.ignore_elems = ['outputs', 'tests']
        # self.parsable_elems = ['description', 'command', 'param', 'repeat', 'help', 'citations']

        # tool metadata
        # self.tool_name: str = ''
        # self.tool_id: str = ''
        # self.tool_version: str = ''
        # self.tool_creator: str = ''
        # self.citations: list[dict[str, str]] = []
        # self.requirements: list[dict[str, Union[str, int]]] = []
        # self.main_requirement: dict[str, Union[str, int]] = {}
        # self.container: dict[str, str] = {}
        # self.description: str = ''
        # self.help: str = ''

        # param and output parsing
        # self.tree_path: list[str] = []
        # self.tokens: dict[str, str] = {}
        # self.command_lines: list[str] = [] 
        # self.configfiles: list[Configfile] = []
        # self.command: Command = Command() 
    

    def parse(self) -> None:
        """
        May be a need for a postprocessing step after annotate_datatypes
        to do stuff like confirm the base command etc
        """
        # basic setup
        self.set_metadata()
        self.set_container()

        # gathering UI variables
        self.set_param_register()
        self.set_out_register()
        #self.set_configfiles()
        
        # the business
        self.set_tests()
        self.set_command()

        # post
        self.annotate_datatypes()
        self.write_janis()



    def set_metadata(self):
        meta = Metadata(self.gxtool)
        self.tool.update_metadata(meta)

    
    def set_container(self):
        cf = ContainerFetcher(self.tool, self.logger)
        self.tool.container = cf.fetch()


    # 4th step: param parsing
    def set_param_register(self):
        self.tool.param_register = ParamRegister(self.gxtool.inputs)


    # 5th step: output parsing
    def set_out_register(self):
        self.tool.out_register = OutputRegister(self.gxtool.outputs)


    # 6th step: configfile parsing
    def set_configfiles(self):
        self.tool.configfiles = self.gxtool.config_files


    def set_tests(self):
        self.tool.tests = self.gxtool.tests


    # 7th step: command parsing 
    def set_command(self):
        cmdpar = CommandParser(self.gxtool, self.tool, self.logger)
        workflow_step = None
        cmdpar.parse(workflow_step=workflow_step)
        self.command = cmdpar.command


    # 8th step: annotating with datatypes
    def annotate_datatypes(self):
        da = DatatypeAnnotator(self.tool, self.logger)
        da.annotate()
        if self.debug:
            self.command.pretty_print()


    # 9th step: convert to janis definition & write
    def write_janis(self):
        # generate janis py
        jf = JanisFormatter(self.tool, self.janis_out_path, self.logger) # type: ignore
        jf.format()
        jf.write()









"""
SHAME CORNER

    # 1st step: macro expansion (preprocessing)
    def parse_macros(self) -> None:
        mp = MacroXMLParser(self.workdir, self.filename, self.logger)
        mp.parse()
        self.tree = mp.tree 
        
        # update the xml tree
        self.tokens.update(mp.tokens)
        self.root = self.tree.getroot()
        self.check_macro_expansion(self.root)


    # 2nd step: token handling (preprocessing)
    def parse_tokens(self):
        tp = TokenXMLParser(self.tree, self.tokens, self.logger)
        tp.parse()
        self.tree = tp.tree


def set_metadata(self):
        mp = MetadataXMLParser(self.tree, self.logger)
        mp.parse()
        self.tool_name = mp.tool_name
        self.tool_id = mp.tool_id
        self.tool_version = mp.tool_version
        self.description = mp.description
        self.requirements = mp.requirements
        self.citations = mp.citations
        self.help = mp.help


    # 4th step: param parsing
    def set_param_register(self):
        pp = ParamXMLParser(self.tree, self.logger)
        params = pp.parse()
        if self.debug:
            pp.pretty_print()
        self.param_register.add(params)


    # 5th step: output parsing
    def set_out_register(self):
        op = OutputXMLParser(self.tree, self.param_register, self.logger)
        outputs = op.parse() 
        if self.debug:
            op.pretty_print()
        self.out_register.add(outputs)


    # 6th step: configfile parsing
    def set_configfiles(self):
        cp = ConfigfileXMLParser(self.tree, self.tokens, self.logger)
        cp.parse()
        self.configfiles = cp.configfiles


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


"""