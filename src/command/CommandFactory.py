



from command.Command import Command
from command.cmdstr.CommandString import CommandString
from tool.tool_definition import GalaxyToolDefinition




class CommandFactory:
    tool: GalaxyToolDefinition
    cmdstrs: list[CommandString]
    num_ingested_cmdstrs: int

    def create(self, command_line_strings: list[CommandString], tool: GalaxyToolDefinition) -> Command:
        self.refresh_attributes(command_line_strings, tool)

    def refresh_attributes(self, command_line_strings: list[CommandString], tool: GalaxyToolDefinition) -> None:
        self.tool = tool
        self.cmdstrs = command_line_strings
        self.num_ingested_cmdstrs = 0



