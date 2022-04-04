



from dataclasses import dataclass
from typing import Optional
from command.cmdstr.CommandString import CommandString
from command.components.CommandComponent import CommandComponent
from command.components.inputs.Flag import Flag
from command.components.inputs.Option import Option
from command.components.inputs.Positional import Positional
from containers.Container import Container
from tags.TagManager import ToolTagManager
from xmltool.ToolXMLMetadata import ToolXMLMetadata
from janis.formatters.JanisToolFormatter import JanisToolFormatter
from xmltool.param.InputParamRegister import InputParamRegister
from xmltool.param.Param import Param
from uuid import uuid4



@dataclass
class Tool:
    """
    a Tool() is the final representation of the software tool
    a galaxy XML wrapper is running. Includes metadata, inputs, outputs, a container to execute the tool, base command etc. 
    """
    metadata: ToolXMLMetadata
    xmlcmdstr: CommandString
    gxparam_register: InputParamRegister
    inputs: list[CommandComponent]
    outputs: list[CommandComponent]
    container: Optional[Container]
    base_command: list[str]
    tag_manager: ToolTagManager = ToolTagManager()

    def __post_init__(self):
        self.uuid: str = str(uuid4())
        self.register_tool_tag()

    def register_tool_tag(self) -> None:
        self.tag_manager.register(
                tag_type='tool_name',
                uuid=self.get_uuid(),
                entity_info={
                    'name': self.metadata.id
                }
            )

    def register_component_tags(self) -> None:
        for component in self.inputs + self.outputs:
            self.tag_manager.register(
                tag_type='tool_component',
                uuid=component.get_uuid(),
                entity_info={
                    'name': component.get_name(),
                    'datatype': component.janis_datatypes[0].classname
                }
            )

    def get_uuid(self) -> str:
        return self.uuid

    def get_gxparam(self, query: str) -> Optional[Param]:
        param = self.gxparam_register.get(query, strategy='lca')
        if not param:
            pass
            #raise RuntimeError(f'no gxparam named {query}')
        return param
   
    def get_input(self, query_tag: str) -> CommandComponent:
        for inp in self.inputs:
            tag = self.tag_manager.get('tool_component', inp.get_uuid())
            if query_tag == tag:
                return inp
        raise RuntimeError(f'could not find {query_tag} in tool inputs')

    def get_inputs(self) -> dict[str, CommandComponent]:
        return {self.tag_manager.get('tool_component', inp.get_uuid()): inp for inp in self.inputs}

    def get_positionals(self) -> list[Positional]:
        return [x for x in self.inputs if isinstance(x, Positional)]

    def get_flags(self) -> list[Flag]:
        return [x for x in self.inputs if isinstance(x, Flag)]

    def get_options(self) -> list[Option]:
        return [x for x in self.inputs if isinstance(x, Option)]

    def get_outputs(self) -> dict[str, CommandComponent]:
        return {self.tag_manager.get('tool_component', out.get_uuid()): out for out in self.outputs}

    def get_preprocessing(self) -> Optional[str]:
        raise NotImplementedError

    def get_postprocessing(self) -> Optional[str]:
        raise NotImplementedError

    def to_janis_definition(self) -> str:
        formatter = JanisToolFormatter()
        str_note = formatter.format_top_note(self.metadata)
        str_path = formatter.format_path_appends()
        str_metadata = formatter.format_metadata(self.metadata)
        str_inputs = formatter.format_inputs(self.get_inputs())
        str_outputs = formatter.format_outputs(self.get_outputs())
        str_commandtool = formatter.format_commandtool(self.metadata, self.base_command, self.container)
        str_translate = formatter.format_translate_func(self.metadata) 
        str_imports = formatter.format_imports()
        return str_note + str_path + str_imports + str_metadata + str_inputs + str_outputs + str_commandtool + str_translate
    


    
