

from typing import Any
from command.components.CommandComponent import CommandComponent
from command.components.outputs import InputOutput, WildcardOutput
from command.components.outputs.UnknownOutput import UnknownOutput
from datatypes.JanisDatatype import JanisDatatype

selector_map: dict[Any, str] = {
    InputOutput: 'from janis_core import InputSelector',
    WildcardOutput: 'from janis_core import WildcardSelector',
    UnknownOutput: 'from janis_core import WildcardSelector',
}

default_import_str = """
from janis_core import (
    CommandToolBuilder, 
    ToolMetadata,
    ToolInput, 
    ToolOutput,
    Array,
    Optional,
    UnionType,
    Stdout
)
"""


SelectorOutputs = InputOutput | WildcardOutput | UnknownOutput


class ToolImportHandler:
    def __init__(self):
        self.datatype_imports: set[str] = set() 
        self.selector_imports: set[str] = set()
    
    def update(self, component: CommandComponent) -> None:
        self.update_datatype_imports(component.janis_datatypes)
        if isinstance(component, SelectorOutputs):
            self.update_selector_imports(component)

    def update_datatype_imports(self, janis_types: list[JanisDatatype]) -> None: 
        for jtype in janis_types:
            import_str = f'from {jtype.import_path} import {jtype.classname}'
            self.datatype_imports.add(import_str)

    def update_selector_imports(self, comp: SelectorOutputs) -> None:
        import_path = selector_map[type(comp)]
        self.selector_imports.add(import_path)

    def imports_to_string(self) -> str:
        out_str: str = ''
        out_str += default_import_str
        out_str += self.datatype_imports_to_str()
        out_str += self.selector_imports_to_str()
        return out_str + '\n'

    def datatype_imports_to_str(self) -> str:
        out_str: str = ''
        for d_import in self.datatype_imports:
            out_str += f'{d_import}\n'
        return out_str

    def selector_imports_to_str(self) -> str:
        out_str: str = ''
        for d_import in self.selector_imports:
            out_str += f'{d_import}\n'
        return out_str
            
        


        
