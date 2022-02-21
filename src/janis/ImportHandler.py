

from command.components.CommandComponent import CommandComponent
from tool.param.OutputParam import OutputParam
from tool.parsing.selectors import SelectorType
from janis.DatatypeRegister import DatatypeRegister
from command.components.linux_constructs import Redirect

default_import_str = """
from janis_core import (
    CommandToolBuilder, 
    ToolInput, 
    ToolOutput,
    Array,
    Optional,
    UnionType,
    Stdout
)
"""

selector_map: dict[SelectorType, str] = {
    SelectorType.INPUT_SELECTOR: 'from janis_core import InputSelector',
    SelectorType.WILDCARD_SELECTOR: 'from janis_core import WildcardSelector',
    SelectorType.STRING_FORMATTER: 'from janis_core import StringFormatter'
}

class ImportHandler:
    def __init__(self, datatype_register: DatatypeRegister):
        self.datatype_imports: set[str] = set() 
        self.selector_imports: set[str] = set()
        self.datatype_register = datatype_register

    def update(self, component: CommandComponent):
        self.update_datatype_imports(component)
        self.update_selector_imports(component)

    def update_datatype_imports(self, component: CommandComponent): 
        raw_datatype = component.get_datatype()
        janis_types = self.datatype_register.get(raw_datatype)
        for jtype in janis_types:
            import_str = f'from {jtype.import_path} import {jtype.classname}'
            self.datatype_imports.add(import_str)

    def update_selector_imports(self, component: CommandComponent):
        if isinstance(component, Redirect):
            selector = component.get_selector()
            import_path = selector_map[selector.stype]
            self.selector_imports.add(import_path)
        elif isinstance(component.gxvar, OutputParam):
            if component.gxvar.selector:
                import_path = selector_map[component.gxvar.selector.stype]
                self.selector_imports.add(import_path)

    def imports_to_string(self) -> str:
        out_str: str = ''
        out_str += default_import_str
        out_str += self.datatype_imports_to_str()
        out_str += self.selector_imports_to_str()
        return out_str

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
            
        


        
