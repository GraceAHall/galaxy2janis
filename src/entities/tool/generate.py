

from typing import Optional
from gx.gxtool.load import XMLToolDefinition
from shellparser.command import Command
from entities.tool import Tool
from entities.tool.ToolFactory import ToolFactory


def gen_tool(xmltool: XMLToolDefinition, command: Command, container: Optional[str]) -> Tool:
    factory = ToolFactory(xmltool, command, container)
    tool = factory.create()
    return tool

