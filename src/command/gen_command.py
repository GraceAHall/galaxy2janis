


from command.CommandFactory import CommandFactory
from runtime.settings.ExeSettings import ToolExeSettings
from xmltool.XMLToolDefinition import XMLToolDefinition
from command.Command import Command



def gen_command(esettings: ToolExeSettings, xmltool: XMLToolDefinition) -> Command:
    factory = CommandFactory(esettings, xmltool)
    return factory.create()

