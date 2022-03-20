



from dataclasses import dataclass
from typing import Optional
from command.cmdstr.CommandString import CommandString
from command.components.CommandComponent import CommandComponent
from containers.Container import Container
from xmltool.metadata import Metadata
from janis_definition.JanisFormatter import JanisFormatter


@dataclass
class Tool:
    metadata: Metadata
    xmlcmdstr: CommandString
    inputs: list[CommandComponent]
    outputs: list[CommandComponent]
    container: Optional[Container]
    base_command: list[str]

    def get_inputs(self) -> list[CommandComponent]:
        return self.inputs
    
    def get_outputs(self) -> list[CommandComponent]:
        return self.outputs

    def get_preprocessing(self) -> Optional[str]:
        raise NotImplementedError

    def get_postprocessing(self) -> Optional[str]:
        raise NotImplementedError

    def to_janis_definition(self) -> str:
        formatter = JanisFormatter()
        str_path = formatter.format_path_appends()
        str_inputs = formatter.format_inputs(self.get_inputs())
        str_outputs = formatter.format_outputs(self.get_outputs())
        str_commandtool = formatter.format_commandtool(self.metadata, self.base_command, self.container)
        str_translate = formatter.format_translate_func(self.metadata) 
        str_imports = formatter.format_imports()
        return str_path + str_imports + str_inputs + str_outputs + str_commandtool + str_translate



    
