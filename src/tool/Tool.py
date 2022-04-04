



from dataclasses import dataclass
from typing import Optional
from command.cmdstr.CommandString import CommandString
from command.components.CommandComponent import CommandComponent
from command.components.inputs.Flag import Flag
from command.components.inputs.Option import Option
from command.components.inputs.Positional import Positional
from containers.Container import Container
from xmltool.ToolXMLMetadata import ToolXMLMetadata
from janis.formatters.JanisToolFormatter import JanisToolFormatter
from xmltool.param.InputParamRegister import InputParamRegister
from xmltool.param.Param import Param
from uuid import uuid4


@dataclass
class Tool:
    metadata: ToolXMLMetadata
    xmlcmdstr: CommandString
    inputs: list[CommandComponent]
    outputs: list[CommandComponent]
    container: Optional[Container]
    base_command: list[str]
    gxparam_register: InputParamRegister
    uuid: str = str(uuid4())

    def get_gxparam(self, query: str) -> Optional[Param]:
        param = self.gxparam_register.get(query, strategy='lca')
        if not param:
            pass
            #raise RuntimeError(f'no gxparam named {query}')
        return param
   
    def list_inputs(self) -> list[CommandComponent]:
        return self.inputs

    def get_input(self, query_tag: str) -> CommandComponent:
        for inp in self.inputs:
            if query_tag == inp.get_janis_tag():
                return inp
        raise RuntimeError(f'could not find {query_tag} in tool inputs')

    def get_inputs_by_component_type(self) -> dict[str, list[CommandComponent]]:
        return {
            'positionals': self.get_positionals(),
            'flags': self.get_flags(),
            'options': self.get_options()
        }

    def get_positionals(self) -> list[Positional]:
        return [x for x in self.inputs if isinstance(x, Positional)]

    def get_flags(self) -> list[Flag]:
        return [x for x in self.inputs if isinstance(x, Flag)]

    def get_options(self) -> list[Option]:
        return [x for x in self.inputs if isinstance(x, Option)]

    def list_outputs(self) -> list[CommandComponent]:
        return self.outputs

    def get_preprocessing(self) -> Optional[str]:
        raise NotImplementedError

    def get_postprocessing(self) -> Optional[str]:
        raise NotImplementedError

    def to_janis_definition(self) -> str:
        formatter = JanisToolFormatter()
        str_note = formatter.format_top_note(self.metadata)
        str_path = formatter.format_path_appends()
        str_metadata = formatter.format_metadata(self.metadata)
        str_inputs = formatter.format_inputs(self.get_inputs_by_component_type())
        str_outputs = formatter.format_outputs(self.list_outputs())
        str_commandtool = formatter.format_commandtool(self.metadata, self.base_command, self.container)
        str_translate = formatter.format_translate_func(self.metadata) 
        str_imports = formatter.format_imports()
        return str_note + str_path + str_imports + str_metadata + str_inputs + str_outputs + str_commandtool + str_translate



    
