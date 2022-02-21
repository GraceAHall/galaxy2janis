

from typing import Tuple

from galaxy_interaction import GalaxyManager
from tool.tool_definition import GalaxyToolDefinition

from command.cmdstr.ToolExecutionString import ToolExecutionString, ToolExecutionStringFactory
from command.Command import Command
from command.CommandFactory import CommandFactory


def infer_command(gxmanager: GalaxyManager, tool: GalaxyToolDefinition) -> Command:
    raw_strings: list[Tuple[str, str]] = gxmanager.get_raw_cmdstrs(tool)
    cmd_strings = generate_cmd_strings(raw_strings, tool)
    command = generate_cmd(cmd_strings, tool)
    return command

def generate_cmd_strings(raw_strings: list[Tuple[str, str]], tool: GalaxyToolDefinition) -> list[ToolExecutionString]:
    cmdstr_fac = ToolExecutionStringFactory(tool)
    cmd_strings = [cmdstr_fac.create(source, raw_str) for source, raw_str in raw_strings]
    return cmd_strings

def generate_cmd(cmd_strings: list[ToolExecutionString], tool: GalaxyToolDefinition) -> Command:
    cmd_fac = CommandFactory(tool)
    command = cmd_fac.create(cmd_strings)
    return command