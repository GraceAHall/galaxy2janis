


from typing import Optional
from janis.JanisFormatter import JanisFormatter
from runtime.settings import ExecutionSettings
from tool.tool import GalaxyToolDefinition
from command.infer import Command
from containers.fetch import Container


def write_janis(esettings: ExecutionSettings, tool: GalaxyToolDefinition, command: Command, container: Optional[Container]) -> None:
    formatter = JanisFormatter(esettings)
    imports_str = formatter.format_imports(command)
    inputs_str = formatter.format_inputs(command)
    outputs_str = formatter.format_outputs(command)
    commandtool_str = formatter.format_commandtool(tool, command, container) #TODO container Optionality None
    translate_str = formatter.format_translate_func(tool) 
