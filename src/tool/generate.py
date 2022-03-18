

from xmltool.load import XMLToolDefinition
from command.infer import Command
from containers.fetch import Container
from tool.Tool import Tool


def generate_tool(xmltool: XMLToolDefinition, command: Command, container: Container) -> Tool:
    raise NotImplementedError