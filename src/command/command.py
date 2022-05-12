


from command.CommandFactory import CommandFactory
from startup.ExeSettings import ToolExeSettings
from xmltool.tool_definition import XMLToolDefinition
from command.Command import Command



def gen_command(esettings: ToolExeSettings, xmltool: XMLToolDefinition) -> Command:
    factory = CommandFactory(esettings, xmltool)
    return factory.create()

