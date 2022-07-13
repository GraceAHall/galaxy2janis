

import logs.logging as logging
from typing import Optional

from gx.gxtool.load import XMLToolDefinition
from gx.text import load_command
from gx.text import load_partial_cheetah_command

from command import Command

# this module imports
from .Tool import Tool
from .outputs import extract_outputs


class ToolFactory:
    def __init__(self, xmltool: XMLToolDefinition, command: Command, container: Optional[str]) -> None:
        self.xmltool = xmltool
        self.command = command
        self.container = container

    def create(self) -> Tool:
        command_text = self.get_command()
        
        tool = Tool(
            metadata=self.xmltool.metadata,
            container=self.container,
            base_command=self.get_base_command(),
            gxparam_register=self.xmltool.inputs,
            command=self.get_command(),
            preprocessing=self.get_preprocessing(),
            postprocessing=self.get_postprocessing(),
        )
        self.supply_inputs(tool)
        self.supply_outputs(tool)
        return tool

    def get_preprocessing(self) -> Optional[str]:
        self.command.xmlcmdstr.preprocessing

        raise NotImplementedError()
    
    def get_postprocessing(self) -> Optional[str]:
        self.command.xmlcmdstr.postprocessing
        
        raise NotImplementedError()

    def supply_inputs(self, tool: Tool) -> None:
        self.command.set_cmd_positions()
        inputs = self.command.list_inputs(include_base_cmd=False)
        if not inputs:
            logging.no_inputs()
        for inp in inputs:
            tool.add_input(inp)

    def supply_outputs(self, tool: Tool) -> None:
        outputs = extract_outputs(self.xmltool, self.command)
        if not outputs:
            logging.no_outputs()
        for out in outputs:
            tool.add_output(out)

    def get_base_command(self) -> list[str]:
        positionals = self.command.get_base_positionals()
        if not positionals:
            logging.no_base_cmd()
        return [p.default_value for p in positionals]
    