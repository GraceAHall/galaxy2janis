

from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4
from gx.configfiles.Configfile import Configfile

from gx.gxtool.ToolXMLMetadata import ToolXMLMetadata
from gx.gxtool.param.ParamRegister import ParamRegister
from gx.gxtool.param.Param import Param

from gx.command.components import CommandComponent
from gx.command.components import InputComponent
from gx.command.components import OutputComponent

import tags


# shouldn't really be a dataclass, just annoying to write __init__ method
@dataclass
class Tool:
    """
    a Tool() is the final representation of the software tool
    a galaxy XML wrapper is running. Includes metadata, inputs, outputs, a container to execute the tool, base command etc. 
    """
    uuid: str = field(init=False)
    metadata: ToolXMLMetadata
    gxparam_register: ParamRegister
    configfiles: list[Configfile]
    container: Optional[str]
    base_command: list[str]

    def __post_init__(self):
        self.inputs: list[InputComponent] = []
        self.outputs: list[OutputComponent] = []
        self.uuid: str = str(uuid4())
        tags.new_group('tool', self.uuid)
        tags.register(self)

    def add_input(self, inp: InputComponent) -> None:
        tags.switch_group(self.uuid)
        tags.register(inp)
        self.inputs.append(inp)
    
    def add_output(self, out: OutputComponent) -> None:
        tags.switch_group(self.uuid)
        tags.register(out)
        self.outputs.append(out)

    def get_gxparam(self, query: str) -> Optional[Param]:
        param = self.gxparam_register.get(query, strategy='lca')
        if not param:
            pass
            #raise RuntimeError(f'no gxparam named {query}')
        return param
   
    def get_input(self, query_uuid: str) -> Optional[CommandComponent]:
        for inp in self.inputs:
            if query_uuid == inp.uuid:
                return inp
        raise RuntimeError(f'could not find {query_uuid} in tool inputs')
    
    def get_input_via_param_name(self, query_uuid: str) -> CommandComponent:
        for inp in self.inputs:
            if query_uuid == inp.uuid:
                return inp
        raise RuntimeError(f'could not find {query_uuid} in tool inputs')

    def get_preprocessing(self) -> Optional[str]:
        raise NotImplementedError

    def get_postprocessing(self) -> Optional[str]:
        raise NotImplementedError



    
