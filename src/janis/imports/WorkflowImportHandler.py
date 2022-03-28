

from datatypes.JanisDatatype import JanisDatatype


default_class_imports = {
    'janis_core': set([
        'WorkflowBuilder', 
        'WorkflowMetadata',
    ])
}
default_datatype_imports = {
    'janis_core.types.common_data_types': set([
        'File', 
    ])
}

class WorkflowImportHandler:
    def __init__(self):
        self.class_imports: dict[str, set[str]] = default_class_imports
        self.tool_imports: dict[str, set[str]] = {}
        self.datatype_imports: dict[str, set[str]] = default_datatype_imports 

    def update_class_imports(self, import_path: str, import_name: str) -> None: 
        if import_path not in self.class_imports:
            self.class_imports[import_path] = set()
        self.class_imports[import_path].add(import_name)
    
    def update_tool_imports(self, import_path: str, import_name: str) -> None: 
        if import_path not in self.class_imports:
            self.tool_imports[import_path] = set()
        self.tool_imports[import_path].add(import_name)
    
    def update_datatype_imports(self, janis_types: list[JanisDatatype]) -> None: 
        for jtype in janis_types:
            if jtype.import_path not in self.class_imports:
                self.datatype_imports[jtype.import_path] = set()
            self.datatype_imports[jtype.import_path].add(jtype.classname)

    def imports_to_string(self) -> str:
        out_str: str = ''
        for import_dict in [self.class_imports, self.datatype_imports, self.tool_imports]:
            if len(import_dict) > 0:
                out_str += self._format_import_dict(import_dict)
        return out_str + '\n'

    def _format_import_dict(self, import_dict: dict[str, set[str]]) -> str:
        out_str: str = ''
        for import_path, import_names in import_dict.items():
            if len(import_names) > 2:
                out_str += self._format_accordion(import_path, import_names)
            else:
                out_str += self._format_flat(import_path, import_names)
        out_str += '\n'
        return out_str

    def _format_accordion(self, import_path: str, import_names: set[str]) -> str:
        out_str = f'from {import_path} import ('
        for import_name in self._set_to_ordered_list(import_names):
            out_str += f'{import_name}\n'
        out_str += ')'
        return out_str
    
    def _format_flat(self, import_path: str, import_names: set[str]) -> str:
        out_str: str = ''
        for import_name in self._set_to_ordered_list(import_names):
            out_str += f'from {import_path} import {import_name}\n'
        return out_str

    def _set_to_ordered_list(self, import_names: set[str]) -> list[str]:
        imports_list = list(import_names)
        imports_list.sort(key=lambda x: len(x))
        return imports_list

