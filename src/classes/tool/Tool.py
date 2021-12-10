

from typing import Union, Optional


from classes.command.Command import Command
from classes.params.ParamRegister import ParamRegister
from classes.outputs.OutputRegister import OutputRegister
from classes.metadata.Metadata import Metadata


class Tool:
    def __init__(self):
        self.name: str = ""
        self.id: str = ""
        self.version: str = ""
        self.creator: Optional[str] = None
        self.help: str = ""
        self.tool_module: str = 'bioinformatics' 

        self.requirements: Optional[list[dict[str, Union[str, int]]]] = None
        self.main_requirement: Optional[dict[str, Union[str, int]]] = None
        self.citations: list[dict[str, str]] = []
        self.container: Optional[dict[str, str]] = None

        self.tests: Optional[str] = None
        self.command: Optional[Command] = None  
        self.param_register: Optional[ParamRegister] = None
        self.out_register: Optional[OutputRegister] = None


    def update_metadata(self, meta: Metadata) -> None:
        self.transfer_attributes(meta)
        self.version = self.version.rsplit('+galaxy', 1)[0]


    def transfer_attributes(self, meta: Metadata) -> None:
        for k, v in meta.__dict__.items():
            self.__dict__[k] = v


    # def get_help(self) -> str:
    #     return repr(self.help)