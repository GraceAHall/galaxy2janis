

from abc import ABC, abstractmethod

from datatypes.JanisDatatype import JanisDatatype
from workflows.step.WorkflowStep import WorkflowStep
from workflows.workflow.Workflow import Workflow
from .Import import Import


class SortStrategy(ABC):
    @abstractmethod
    def sort(self, imports: list[Import]) -> list[Import]:
        ...

class AlphabeticalSortStrategy(SortStrategy):
    def sort(self, imports: list[Import]) -> list[Import]:
        imports.sort(key=lambda x: f'{x.path}.{x.entity}')
        return imports

class LengthSortStrategy(SortStrategy):
    def sort(self, imports: list[Import]) -> list[Import]:
        imports.sort(key=lambda x: len(f'{x.path}.{x.entity}'), reverse=True)
        return imports


default_class_imports = [
    Import(path='janis_core', entity='WorkflowBuilder'),
    Import(path='janis_core', entity='WorkflowMetadata')
]

default_datatype_imports = [
    Import(path='janis_core.types.common_data_types', entity='File'),
]


class WorkflowImportCollector:
    def __init__(self):
        self.imports: dict[str, Import] = dict()
    
    def update(self, imports: list[Import]) -> None:
        for imp in imports:
            key = f'{imp.path}.{imp.entity}'
            if key not in self.imports:
                self.imports[key] = imp
    
    def list_imports(self) -> list[Import]:
        sort_strategies = [
            AlphabeticalSortStrategy(),
            LengthSortStrategy(),
        ]
        imports = list(self.imports.values())
        for strategy in sort_strategies:
            imports = strategy.sort(imports)
        return imports

    def collect_workflow_imports(self, workflow: Workflow) -> None:
        workflow_imports: list[Import] = []
        workflow_imports += default_class_imports
        workflow_imports += default_datatype_imports
        workflow_imports += self.get_imports_from_inputs(workflow)
        workflow_imports += self.get_imports_from_outputs(workflow)
        self.update(workflow_imports)

    def collect_step_imports(self, step: WorkflowStep, workflow: Workflow) -> None:
        step_imports: list[Import] = []
        step_imports.append(self.get_tool_definition_import(step, workflow))
        step_imports += self.get_runtime_input_imports(step)
        self.update(step_imports)
        
    def get_imports_from_inputs(self, workflow: Workflow) -> list[Import]:
        imports: list[Import] = []
        for inp in workflow.inputs:
            imports += self.get_datatype_imports(inp.janis_datatypes)
        return imports
    
    def get_datatype_imports(self, janis_types: list[JanisDatatype]) -> list[Import]:
        imports: list[Import] = [] 
        for jtype in janis_types:
            imports.append(Import(path=jtype.import_path, entity=jtype.classname))
        return imports
    
    def get_imports_from_outputs(self, workflow: Workflow) -> list[Import]:
        imports: list[Import] = []
        for out in workflow.outputs:
            imports += self.get_datatype_imports(out.janis_datatypes)
        return imports

    def get_tool_definition_import(self, step: WorkflowStep, workflow: Workflow) -> Import:
        tool_path = step.get_definition_path()
        tool_path = tool_path.rsplit('.py')[0]
        tool_path = tool_path.replace('/', '.')
        tool_tag = workflow.tag_manager.get(step.tool.get_uuid())
        tool_tag = tool_tag.rstrip('123456789') # same as getting basetag, just dodgy method
        return Import(path=tool_path, entity=tool_tag)

    def get_runtime_input_imports(self, step: WorkflowStep) -> list[Import]:
        raise NotImplementedError()
    




"""
    # FORMATTING AND STR REPRESENTATION

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


    # STEP RELATED



    def update_imports_for_tool_outputs(self, step: WorkflowStep) -> None:
        pass
    
    def update_tool_imports(self, import_path: str, import_name: str) -> None: 
        if import_path not in self.class_imports:
            self.tool_imports[import_path] = set()
        self.tool_imports[import_path].add(import_name)




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


"""