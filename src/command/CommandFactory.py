


from startup.ExeSettings import ToolExeSettings
from xmltool.tool_definition import XMLToolDefinition
from galaxy_interaction import GalaxyManager

from command.manipulation import simplify_test, simplify_xml
from command.cmdstr.CommandString import CommandString
from command.cmdstr.cmdstr import gen_command_string

from command.ArgumentCommandAnnotator import ArgumentCommandAnnotator
from command.CmdstrCommandAnnotator import CmdstrCommandAnnotator

from command.Command import Command


class CommandFactory:
    def __init__(self, esettings: ToolExeSettings, xmltool: XMLToolDefinition):
        self.esettings = esettings
        self.xmltool = xmltool
        self.command = Command()

    def create(self) -> Command:
        self.update_command_via_arguments()
        self.update_command_via_cmdstrs()
        return self.command

    def update_command_via_arguments(self) -> None:
        """uses galaxy params with an 'argument' attribute to update command"""
        annotator = ArgumentCommandAnnotator(self.command, self.xmltool)
        annotator.annotate()
    
    def update_command_via_cmdstrs(self) -> None:
        """
        uses valid command line strings from tests, and the tool XML <command> section
        to further identify the structure and options of the underling software tool
        """
        # create command strings (from evaluated tests, simplified xml <command>)
        cmdstrs = self.gen_cmdstrs()
        annotator = CmdstrCommandAnnotator(self.command, self.xmltool, cmdstrs)
        annotator.annotate()

    def gen_cmdstrs(self) -> list[CommandString]:
        # note ordering: xml then test
        xml_cmdstr = self.gen_cmdstr_from_xml()
        test_cmdstrs = self.gen_cmdstrs_from_tests()
        cmdstrs = [xml_cmdstr] + test_cmdstrs
        return cmdstrs

    def gen_cmdstr_from_xml(self) -> CommandString:
        gxmanager = GalaxyManager(self.esettings)
        cmdstr = gxmanager.get_xml_cmdstr(self.xmltool)
        cmdstr = simplify_xml(cmdstr)
        return gen_command_string(source='xml', the_string=cmdstr, xmltool=self.xmltool)

    def gen_cmdstrs_from_tests(self) -> list[CommandString]:
        cmdstrs: list[CommandString] = []
        gxmanager = GalaxyManager(self.esettings)
        for teststr in gxmanager.get_test_cmdstrs(self.xmltool):
            teststr = simplify_test(teststr)
            cmdstr = gen_command_string(source='test', the_string=teststr, xmltool=self.xmltool)
            cmdstrs.append(cmdstr)
        return cmdstrs

