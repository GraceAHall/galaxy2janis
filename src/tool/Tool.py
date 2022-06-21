



from dataclasses import dataclass, field
from typing import Optional
from command.components.CommandComponent import CommandComponent
from containers import Container
from tags import ToolTagManager
from xmltool.ToolXMLMetadata import ToolXMLMetadata
from xmltool.param.InputParamRegister import InputParamRegister
from xmltool.param.Param import Param
from uuid import uuid4


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
    container: Optional[Container]
    base_command: list[str]
    inputs: list[CommandComponent] = field(default_factory=list)
    outputs: list[CommandComponent] = field(default_factory=list)
    tag_manager: ToolTagManager = field(init=False)

    def __post_init__(self):
        self.uuid: str = str(uuid4())
        self.tag_manager: ToolTagManager = ToolTagManager()
        self.tag_manager.register(self)

    def add_input(self, inp: CommandComponent) -> None:
        self.inputs.append(inp)
        self.tag_manager.register(inp)

    def add_output(self, out: CommandComponent) -> None:
        self.outputs.append(out)
        self.tag_manager.register(out)

    def get_gxparam(self, query: str) -> Optional[Param]:
        param = self.gxparam_register.get(query, strategy='lca')
        if not param:
            pass
            #raise RuntimeError(f'no gxparam named {query}')
        return param
   
    def get_input(self, query_uuid: str) -> CommandComponent:
        for inp in self.inputs:
            if query_uuid == inp.uuid:
                return inp
        raise RuntimeError(f'could not find {query_uuid} in tool inputs')

    def list_inputs(self) -> list[CommandComponent]:
        return self.inputs

    def get_tags_inputs(self) -> dict[str, CommandComponent]:
        return {self.tag_manager.get(inp.uuid): inp for inp in self.inputs}
    
    def list_outputs(self) -> list[CommandComponent]:
        return self.outputs

    def get_tags_outputs(self) -> dict[str, CommandComponent]:
        return {self.tag_manager.get(out.uuid): out for out in self.outputs}

    def get_preprocessing(self) -> Optional[str]:
        raise NotImplementedError

    def get_postprocessing(self) -> Optional[str]:
        raise NotImplementedError



    
