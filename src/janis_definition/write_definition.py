


from typing import Optional
from janis_definition.JanisFormatter import JanisFormatter
from startup.ExeSettings import ToolExeSettings
from xmltool.load import XMLToolDefinition
from command.infer import Command
from containers.fetch import Container


def write_janis(esettings: ToolExeSettings, xmltool: XMLToolDefinition, command: Command, container: Optional[Container]) -> None:
    formatter = JanisFormatter()
    path_str = formatter.format_path_appends()
    inputs_str = formatter.format_inputs(command)
    outputs_str = formatter.format_outputs(xmltool, command)
    commandtool_str = formatter.format_commandtool(xmltool, command, container) #TODO container Optionality None
    translate_str = formatter.format_translate_func(xmltool) 
    imports_str = formatter.format_imports()
    with open(esettings.get_janis_definition_path(), 'w') as fp:
        fp.write(path_str + '\n')
        fp.write(imports_str + '\n')
        fp.write(inputs_str + '\n\n')
        fp.write(outputs_str + '\n')
        fp.write(commandtool_str + '\n')
        fp.write(translate_str + '\n')
