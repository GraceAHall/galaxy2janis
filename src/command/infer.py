



from galaxy_interaction.GalaxyManager import GalaxyManager
from xmltool.tool_definition import XMLToolDefinition

from command.Command import Command
from command.cmdstr.CommandString import CommandString
from command.cmdstr.CommandStringFactory import CommandStringFactory
from command.ArgumentCommandAnnotator import ArgumentCommandAnnotator
from command.CmdstrCommandAnnotator import CmdstrCommandAnnotator


# names are really misleading here. 
def infer_command(gxmanager: GalaxyManager, xmltool: XMLToolDefinition) -> Command:
    ci = CommandInferer(gxmanager, xmltool)
    ci.update_command_from_param_arguments()
    ci.update_command_from_cmdstrs()
    return ci.command


class CommandInferer:

    def __init__(self, gxmanager: GalaxyManager, xmltool: XMLToolDefinition) -> None:
        self.gxmanager = gxmanager
        self.xmltool = xmltool
        self.command = Command()

        self.cmdstrs: list[CommandString] = []
        self.cmdstr_factory = CommandStringFactory(self.xmltool)

    def update_command_from_param_arguments(self) -> None:
        """uses galaxy params with an 'argument' attribute to update command"""
        annotator = ArgumentCommandAnnotator(self.command, self.xmltool)
        annotator.annotate()
    
    def update_command_from_cmdstrs(self) -> None:
        """
        uses valid command line strings from tests, and the tool XML <command> section
        to further identify the structure and options of the underling software tool
        """
        # create command strings (from evaluated tests, simplified xml <command>)
        self.gen_test_cmdstrs()
        self.gen_xml_cmdstr()
        # update command from command strings
        annotator = CmdstrCommandAnnotator(self.command, self.xmltool, self.cmdstrs)
        annotator.annotate()
        
    def gen_test_cmdstrs(self) -> None:
        for test_str in self.gxmanager.get_test_cmdstrs(self.xmltool):
            cmdstr = self.cmdstr_factory.create('test', test_str)
            self.cmdstrs.append(cmdstr)

    def gen_xml_cmdstr(self) -> None:
        xml_str = self.gxmanager.get_xml_cmdstr(self.xmltool)
        cmdstr = self.cmdstr_factory.create('xml', xml_str)
        self.cmdstrs.append(cmdstr)

    def gen_workflow_cmdstr(self) -> str:
        raise NotImplementedError
   
    def print_cmdstrs(self) -> None:
        test_cmdstrs = [x for x in self.cmdstrs if x.source == 'test']
        xml_cmdstrs = [x for x in self.cmdstrs if x.source == 'xml']

        print('\nCommand strings being fed for inference ------------------------')
        print('\nTests:\n')
        for cmdstr in test_cmdstrs:
            cmdstr.main.print_execution_paths()
        print('\n\nXml:\n')
        for cmdstr in xml_cmdstrs:
            cmdstr.main.print_execution_paths()
        print('\n')



