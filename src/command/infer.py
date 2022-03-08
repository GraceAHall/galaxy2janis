

from typing import Tuple

from galaxy_interaction import GalaxyManager
from tool.tool_definition import GalaxyToolDefinition

from command.cmdstr.DynamicCommandString import DynamicCommandString, DynamicCommandStringFactory
from command.Command import Command
from command.BruteForceCommandFactory import BruteForceCommandFactory


def infer_command(gxmanager: GalaxyManager, tool: GalaxyToolDefinition) -> Command:
    ci = CommandInferer(gxmanager, tool)
    ci.load_raw_strings()
    ci.gen_cmd_strings()
    ci.print_cmdstrs()
    ci.gen_command()
    return ci.command


class CommandInferer:
    command: Command
    raw_strs: list[Tuple[str, str]] = []
    cmdstrs: list[DynamicCommandString] = []

    def __init__(self, gxmanager: GalaxyManager, tool: GalaxyToolDefinition) -> None:
        self.gxmanager = gxmanager
        self.tool = tool

    def load_raw_strings(self) -> None:
        self.raw_strs = self.gxmanager.get_raw_cmdstrs(self.tool)

    def gen_cmd_strings(self) -> None:
        factory = DynamicCommandStringFactory(self.tool)
        self.cmdstrs.append(factory.create('xml', self.get_xml_rawstr()))
        self.cmdstrs += [factory.create('test', raw_str) for raw_str in self.get_test_rawstrs()]
        
    def get_test_rawstrs(self) -> list[str]:
        return [rawstr for source, rawstr in self.raw_strs if source == 'test']

    def get_xml_rawstr(self) -> str:
        return [rawstr for source, rawstr in self.raw_strs if source == 'xml'][0]

    def get_workflow_rawstr(self) -> str:
        raise NotImplementedError
   
    def print_cmdstrs(self) -> None:
        test_cmdstrs = [x for x in self.cmdstrs if x.source == 'test']
        xml_cmdstrs = [x for x in self.cmdstrs if x.source == 'xml']

        print('\nCommand strings being fed for inference ------------------------')
        print('\nTests:\n')
        for cmdstr in test_cmdstrs:
            cmdstr.tool_statement.print_execution_paths()
        print('\n\nXml:\n')
        for cmdstr in xml_cmdstrs:
            cmdstr.tool_statement.print_execution_paths()
        print()

    def gen_command(self) -> None:
        factory = BruteForceCommandFactory(self.tool)
        self.command = factory.create(self.cmdstrs)


