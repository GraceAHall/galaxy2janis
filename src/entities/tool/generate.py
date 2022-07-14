

from typing import Optional
from gx.gxtool.load import XMLToolDefinition
from gx.command import Command

# this module imports
from .Tool import Tool
from .ToolFactory import ToolFactory


def gen_tool(xmltool: XMLToolDefinition, command: Command, container: Optional[str]) -> Tool:
    factory = ToolFactory(xmltool, command, container)
    tool = factory.create()
    return tool

