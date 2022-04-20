

from datatypes.JanisDatatype import JanisDatatype
from workflows.workflow.Workflow import Workflow


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

class WorkflowImportCollector:
    def __init__(self):
        self.class_imports: dict[str, set[str]] = default_class_imports
        self.tool_imports: dict[str, set[str]] = {}
        self.datatype_imports: dict[str, set[str]] = default_datatype_imports 

    def collect(self, workflow: Workflow) -> None:
        raise NotImplementedError()

    def update_imports(self, tag: str, component: Any) -> None:
        match component:
            case WorkflowInput():
                self.update_imports_for_workflow_input(component)
            case WorkflowStep():
                self.update_imports_for_tool_step(tag, component)
            case WorkflowOutput():
                self.update_imports_for_workflow_output(component)
            case _:
                pass
    
    def update_imports_for_workflow_input(self, inp: WorkflowInput) -> None:
        self.import_handler.update_datatype_imports(inp.janis_datatypes)
    
    def update_imports_for_tool_step(self, tool_tag: str, step: WorkflowStep) -> None:
        self.update_imports_for_tool_definition(tool_tag, step)
        self.update_imports_for_tool_inputs(step)
        self.update_imports_for_tool_outputs(step)

    def update_imports_for_tool_definition(self, tool_tag: str, step: WorkflowStep) -> None:
        tool_path = step.get_definition_path()
        tool_path = tool_path.rsplit('.py')[0]
        tool_path = tool_path.replace('/', '.')
        tool_tag = tool_tag.rstrip('123456789') # same as getting basetag, just dodgy method
        self.import_handler.update_tool_imports(tool_path, tool_tag)

    def update_imports_for_tool_inputs(self, step: WorkflowStep) -> None:
        pass
        # # get uuids of tool components with value
        # for inp in step():
        # assert(step.tool)
        # component_uuids = [uuid for uuid, _ in step.list_tool_values()]
        # # get component for each uuid
        # components = [c for c in step.tool.inputs if c.get_uuid() in component_uuids]
        # # get datatypes of that component and update
        # for component in components:
        #     self.import_handler.update_datatype_imports(component.janis_datatypes)

    def update_imports_for_tool_outputs(self, step: WorkflowStep) -> None:
        pass
        # # step outputs? this is a little weird
        # for output in step.list_outputs():
        #     self.import_handler.update_datatype_imports(output.janis_datatypes)

    def update_imports_for_workflow_output(self, output: WorkflowOutput) -> None:
        self.import_handler.update_datatype_imports(output.janis_datatypes)


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
            if jtype.import_path not in self.datatype_imports:
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
        out_str = f'from {import_path} import (\n'
        for import_name in self._set_to_ordered_list(import_names):
            out_str += f'\t{import_name},\n'
        out_str += ')\n'
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

