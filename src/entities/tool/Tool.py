

from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

from gx.gxtool.ToolXMLMetadata import ToolXMLMetadata
from gx.gxtool.param.InputParamRegister import InputParamRegister
from gx.gxtool.param.Param import Param

from shellparser.components.CommandComponent import CommandComponent
from shellparser.components.inputs.InputComponent import InputComponent
from shellparser.components.outputs.OutputComponent import OutputComponent

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
    gxparam_register: InputParamRegister
    container: Optional[str]
    base_command: list[str]
    inputs: list[InputComponent] = field(default_factory=list)
    outputs: list[OutputComponent] = field(default_factory=list)

    def __post_init__(self):
        self.uuid: str = str(uuid4())
        tags.tool.new_tool()
        tags.tool.register(self)

    def add_input(self, inp: InputComponent) -> None:
        self.inputs.append(inp)
        tags.tool.register(inp)
    
    def add_output(self, out: OutputComponent) -> None:
        self.outputs.append(out)
        tags.tool.register(out)

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

    def list_inputs(self) -> list[InputComponent]:
        return self.inputs

    def list_outputs(self) -> list[OutputComponent]:
        return self.outputs

    def get_preprocessing(self) -> Optional[str]:
        raise NotImplementedError

    def get_postprocessing(self) -> Optional[str]:
        raise NotImplementedError



    
