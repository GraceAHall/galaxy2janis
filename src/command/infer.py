

from typing import Tuple


from gxmanager import GalaxyManager
from tool.tool_definition import GalaxyToolDefinition
from command.cmdstr.ToolExecutionString import ToolExecutionString, ToolExecutionStringFactory
from command.Command import Command
from command.CommandFactory import CommandFactory


def infer_cmd(gxmanager: GalaxyManager, tooldef: GalaxyToolDefinition) -> Command:
    raw_strings: list[Tuple[str, str]] = gxmanager.get_raw_cmdstrs(tooldef)
    cmd_strings = generate_cmd_strings(raw_strings, tooldef)
    command = generate_cmd(cmd_strings)
    return command

def generate_cmd_strings(raw_strings: list[Tuple[str, str]], tooldef: GalaxyToolDefinition) -> list[ToolExecutionString]:
    cmdstr_fac = ToolExecutionStringFactory(tooldef)
    cmd_strings = [cmdstr_fac.create(source, raw_str) for source, raw_str in raw_strings]
    return cmd_strings

def generate_cmd(cmd_strings: list[ToolExecutionString]) -> Command:
    cmd_fac = CommandFactory()
    command = cmd_fac.create(cmd_strings)
    return command