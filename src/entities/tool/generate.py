

from typing import Optional
from gx.xmltool.load import XMLToolDefinition
from shellparser.command import Command
from containers import Container
from entities.tool import Tool
from entities.tool.ToolFactory import ToolFactory


def gen_tool(xmltool: XMLToolDefinition, command: Command, container: Optional[Container]) -> Tool:
    factory = ToolFactory(xmltool, command, container)
    tool = factory.create()
    return tool

