

from typing import Tuple

from galaxy_interaction import GalaxyManager
from tool.tool_definition import GalaxyToolDefinition

from command.cmdstr.ToolExecutionSource import ToolExecutionSource, ToolExecutionSourceFactory
from command.Command import Command
from command.CommandFactory import CommandFactory




def infer_command(gxmanager: GalaxyManager, tool: GalaxyToolDefinition) -> Command:
    ci = CommandInferer(gxmanager, tool)
    ci.load_raw_strings()
    ci.gen_cmd_strings()
    ci.gen_command()
    return ci.command


class CommandInferer:
    command: Command
    raw_strs: list[Tuple[str, str]] = []
    cmd_strs: list[ToolExecutionSource] = []

    def __init__(self, gxmanager: GalaxyManager, tool: GalaxyToolDefinition) -> None:
        self.gxmanager = gxmanager
        self.tool = tool

    def load_raw_strings(self) -> None:
        self.raw_strs = self.gxmanager.get_raw_cmdstrs(self.tool)

    def gen_cmd_strings(self) -> None:
        factory = ToolExecutionSourceFactory(self.tool)
        self.cmd_strs.append(factory.create('xml', self.get_xml_rawstr()))
        self.cmd_strs += [factory.create('test', raw_str) for raw_str in self.get_test_rawstrs()]
        print()

    def get_test_rawstrs(self) -> list[str]:
        return [rawstr for source, rawstr in self.raw_strs if source == 'test']

    def get_xml_rawstr(self) -> str:
        return [rawstr for source, rawstr in self.raw_strs if source == 'xml'][0]

    def get_workflow_rawstr(self) -> str:
        raise NotImplementedError
   
    def gen_command(self) -> None:
        factory = CommandFactory(self.tool)
        self.command = factory.create(self.cmd_strs)


