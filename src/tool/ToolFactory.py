





from typing import Tuple
from tool.Tool import Tool
from xmltool.load import XMLToolDefinition
from command.infer import Command
from command.components.CommandComponent import CommandComponent
from containers.fetch import Container


class ToolFactory:
    def __init__(self, xmltool: XMLToolDefinition, command: Command, container: Container) -> None:
        self.xmltool = xmltool
        self.command = command
        self.container = container

    def create(self) -> Tool:
        return Tool(
            metadata=self.xmltool.metadata,
            cmdstr=None,
            inputs=self.get_inputs(),
            outputs=self.get_outputs(),
            container=self.container,
            base_command=self.get_base_command()
        )

    def get_inputs(self) -> list[Tuple[int, CommandComponent]]:
        return self.command.get_component_positions()
    
    def get_outputs(self) -> list[CommandComponent]:
        raise NotImplementedError

    def get_base_command(self) -> list[str]:
        raise NotImplementedError
    