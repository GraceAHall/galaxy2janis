
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

from classes.janis.DatatypeExtractor import DatatypeExtractor
from classes.janis.JanisFormatter import JanisFormatter

from classes.logging.Logger import Logger
from classes.tool.GalaxyLoader import GalaxyLoader


"""
This class acts as an orchestrator.
Tool.xml is parsed in a stepwise manner.
"""


from argparse import Namespace
        

class ToolParser:
    def __init__(self, args: Namespace, out_log: str, out_def: str):
        self.filename = args.toolxml
        self.workdir = args.tooldir
        self.wflow = args.wflow
        self.wstep = args.wstep
        self.debug = args.debug
        self.janis_out_path = out_def
        
        self.gx_loader: GalaxyLoader = GalaxyLoader(self.workdir, self.filename)
        self.app: MockApp = self.gx_loader.init_app()
        self.gxtool: GalaxyTool = self.gx_loader.init_tool(self.app)
        self.tool: Tool = Tool()
        
        self.logfile = out_log
        self.logger = Logger(self.logfile)
            

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
        cmdpar = CommandParser(self.app, self.gxtool, self.tool, self.logger)
        self.tool.command = cmdpar.parse(workflow=self.wflow, 
                                    workflow_step=self.wstep)
    

    # 9th step: convert to janis definition & write
    def write_janis(self):
        # generate janis py
        jf = JanisFormatter(self.tool, self.janis_out_path, self.logger) # type: ignore
        jf.format()
        jf.write()



