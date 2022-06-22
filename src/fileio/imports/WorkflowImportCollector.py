

from abc import ABC, abstractmethod

from datatypes import JanisDatatype
from entities.workflow.workflow import WorkflowStep
from entities.workflow.workflow import Workflow
from .Import import Import, ImportType


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
    Import(path='janis_core', entity='WorkflowBuilder', itype=ImportType.JANIS_CLASS),
    Import(path='janis_core', entity='WorkflowMetadata', itype=ImportType.JANIS_CLASS)
]

default_datatype_imports = [
    #Import(path='janis_core.types.common_data_types', entity='File', itype=ImportType.DATATYPE),
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
        """
        workflow inputs include janis classes and datatypes of workflow inputs/outputs
        tool / step imports are handled in collect_step_imports() method
        """
        workflow_imports: list[Import] = []
        workflow_imports += default_class_imports
        workflow_imports += default_datatype_imports
        workflow_imports += self.init_imports_from_inputs(workflow)
        workflow_imports += self.init_imports_from_outputs(workflow)
        self.update(workflow_imports)

    def collect_step_imports(self, step: WorkflowStep, workflow: Workflow) -> None:
        """
        step imports include datatypes in step runtime inputs (workflow inputs)
        and the tool being executed (definition file is external)
        """
        step_imports: list[Import] = []
        step_imports.append(self.init_tool_definition_import(step))
        step_imports += self.init_runtime_input_imports(step, workflow)
        self.update(step_imports)
    
    def collect_page_imports(self, step_paths: list[str]) -> None:
        """
        page imports are the individual steps (when defined in external files)
        """
        page_imports: list[Import] = []
        for path in step_paths:
            page_imports.append(self.init_page_import(path))
        self.update(page_imports)
    
    def init_page_import(self, filepath: str) -> Import:
        import_path = filepath.rsplit('.py', 1)[0]
        import_path = import_path.replace('/', '.')
        return Import(
            path=import_path, 
            entity='*', 
            itype=ImportType.STEP_DEF
        )

    def init_imports_from_inputs(self, workflow: Workflow) -> list[Import]:
        imports: list[Import] = []
        for inp in workflow.inputs:
            imports += self.init_datatype_imports(inp.janis_datatypes)
        return imports
    
    def init_datatype_imports(self, janis_types: list[JanisDatatype]) -> list[Import]:
        imports: list[Import] = [] 
        for jtype in janis_types:
            imports.append(Import(
                path=jtype.import_path, 
                entity=jtype.classname,
                itype=ImportType.DATATYPE
            ))
        return imports
    
    def init_imports_from_outputs(self, workflow: Workflow) -> list[Import]:
        imports: list[Import] = []
        for out in workflow.outputs:
            imports += self.init_datatype_imports(out.janis_datatypes)
        return imports

    def init_tool_definition_import(self, step: WorkflowStep) -> Import:
        tool_path = step.metadata.tool_definition_path
        tool_path = tool_path.rsplit('.py')[0]
        tool_path = tool_path.replace('/', '.')
        tool_tag = step.tool.tag_manager.get(step.tool.uuid)
        return Import(
            path=tool_path, 
            entity=tool_tag,
            itype=ImportType.TOOL_DEF
        )

    def init_runtime_input_imports(self, step: WorkflowStep, workflow: Workflow) -> list[Import]:
        # pulls any datatypes appearing in step runtime inputs (workflow inputs)
        imports: list[Import] = []
        for value in step.tool_values.runtime:
            wflow_input = workflow.get_input(input_uuid=value.input_uuid) 
            assert(wflow_input)
            imports += self.init_datatype_imports(wflow_input.janis_datatypes)
        return imports




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