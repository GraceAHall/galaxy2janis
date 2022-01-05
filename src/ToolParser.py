
# pyright: basic

#import xml.etree.ElementTree as et

from classes.execution.settings import ExecutionSettings
from classes.templating.MockClasses import MockApp
from classes.tool.Tool import Tool
from galaxy.tools import Tool as GalaxyTool

# from classes.tool.MacroXMLParser import MacroXMLParser
# from classes.tool.TokenXMLParser import TokenXMLParser

# xmlparser should be protocol or ABC

from classes.metadata.Metadata import Metadata
from classes.metadata.ContainerFetcher import ContainerFetcher

#from classes.outputs.OutputXMLParser import OutputXMLParser
from classes.outputs.OutputRegister import OutputRegister

#from classes.params.ParamXMLParser import ParamXMLParser
from classes.params.ParamRegister import ParamRegister

from classes.command.CommandParser import CommandParser
from classes.janis.JanisFormatter import JanisFormatter

from classes.logging.Logger import Logger
from classes.tool.GalaxyLoader import GalaxyLoader


"""
This class acts as an orchestrator.
Tool.xml is parsed in a stepwise manner.
"""        

class ToolParser:
    def __init__(self, esettings: ExecutionSettings):
        self.esettings = esettings        
        self.gx_loader: GalaxyLoader = GalaxyLoader(self.esettings)
        self.app: MockApp = self.gx_loader.init_app()
        self.gxtool: GalaxyTool = self.gx_loader.init_tool(self.app)
        self.tool: Tool = Tool()
        self.logger = Logger(self.esettings.get_logfile_path())
            
    def parse(self) -> None:
        """
        May be a need for a postprocessing step after annotate_datatypes
        to do stuff like confirm the base command etc
        """

        self.parse_xml() # returns Tool() regardless of method
        self.generate_cmdline_strings()
        self.infer_command()
        self.write_janis()
        self.write_tests()


        # basic setup
        self.set_metadata()
        self.set_container()

        # gathering galaxy UI variables
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

    def set_param_register(self):
        self.tool.param_register = ParamRegister(self.gxtool.inputs)

    def set_out_register(self):
        self.tool.out_register = OutputRegister(self.gxtool.outputs)

    def set_configfiles(self):
        self.tool.configfiles = self.gxtool.config_files

    def set_tests(self):
        self.tool.tests = self.gxtool.tests

    def set_command(self):
        cmdpar = CommandParser(self.app, self.gxtool, self.tool, self.logger)
        self.tool.command = cmdpar.parse(
            workflow=self.esettings.get_workflow_path(), 
            workflow_step=self.esettings.get_workflow_step()
        )
    
    def write_janis(self):
        # generate janis py
        jf = JanisFormatter(
            self.tool, 
            self.esettings.get_janis_definition_path(), 
            self.logger
        )
        jf.format()
        jf.write()



