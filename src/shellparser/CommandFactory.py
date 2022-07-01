


import settings
from gx.xmltool.XMLToolDefinition import XMLToolDefinition

from shellparser.text.load import load_xml_command, load_test_commands
from shellparser.cmdstr.CommandString import CommandString
from shellparser.cmdstr.cmdstr import gen_command_string

from shellparser.ArgumentCommandAnnotator import ArgumentCommandAnnotator
from shellparser.CmdstrCommandAnnotator import CmdstrCommandAnnotator

from shellparser.Command import Command


class CommandFactory:
    def __init__(self, xmltool: XMLToolDefinition):
        self.xmltool = xmltool
        self.xmlcmdstr = self.gen_cmdstr_from_xml()
        self.command = Command(self.xmlcmdstr)

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
        cmdstrs = [self.xmlcmdstr]
        if settings.general.dev_test_cmdstrs:
            cmdstrs += self.gen_cmdstrs_from_tests()
        return cmdstrs

    def gen_cmdstr_from_xml(self) -> CommandString:
        text = load_xml_command()
        return gen_command_string(source='xml', the_string=text, xmltool=self.xmltool)

    def gen_cmdstrs_from_tests(self) -> list[CommandString]:
        cmdstrs: list[CommandString] = []
        for text in load_test_commands():
            cmdstr = gen_command_string(source='test', the_string=text, xmltool=self.xmltool)
            cmdstrs.append(cmdstr)
        return cmdstrs

