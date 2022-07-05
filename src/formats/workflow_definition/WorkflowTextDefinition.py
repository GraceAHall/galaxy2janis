


from abc import ABC, abstractmethod
from dataclasses import dataclass
import os

from formats.workflow_definition.StepTextDefinition import StepTextDefinition
import settings
from entities.workflow import WorkflowStep
from entities.workflow import Workflow
from formats.imports.WorkflowImportCollector import WorkflowImportCollector
import formats.workflow_definition.snippets as snippets
import formats.workflow_definition.formatting as formatting
from formats.imports.Import import Import


class WorkflowTextDefinition(ABC):
    def __init__(self, workflow: Workflow):
        self.workflow = workflow
        self.step_text_definitions: list[StepTextDefinition] = self.init_step_text_definitions()

    def format(self) -> str:
        out: str = '\n'
        out += self.header
        out += self.imports + '\n'
        out += self.metadata + '\n'
        out += self.declaration + '\n'
        out += self.inputs + '\n'
        for step in self.steps:
            out += step + '\n'
        out += self.outputs + '\n'
        return out
    
    @property
    def header(self) -> str:
        top_note = snippets.gxtool2janis_note_snippet(
            workflow_name=self.workflow.metadata.name,
            workflow_version=self.workflow.metadata.version
        )
        path_appends = snippets.path_append_snippet()
        return f'{top_note}\n{path_appends}\n'

    @property
    def imports(self) -> str:
        imports = self.collect_workflow_imports()
        return formatting.format_imports(imports)
    
    @abstractmethod
    def collect_workflow_imports(self) -> list[Import]:
        """
        collects main workflow page imports. differences:
        BulkWorkflowTextDefinition
            - All datatype imports
            - Tool imports 
        StepwiseWorkflowTextDefinition
            - Non-step datatype imports
            - Step imports (tool imports are in step pages)
        """
        ...
    
    @property
    def metadata(self) -> str:
        metadata = self.workflow.metadata
        return snippets.workflow_metadata_snippet(
            tags=metadata.tags,
            annotation=metadata.annotation,
            version=metadata.version
        )
    
    @property
    def declaration(self) -> str:
        out_str = '# WORKFLOW DECLARATION\n'
        out_str += snippets.workflow_builder_snippet(
            tag=self.workflow.tag_manager.get(self.workflow.uuid),
            version=str(self.workflow.metadata.version),
            doc=self.workflow.metadata.annotation
        )
        return out_str
    
    @property
    def inputs(self) -> str:
        out_str = '# INPUTS\n'
        for inp in self.workflow.inputs:
            tag = self.workflow.tag_manager.get(inp.uuid)
            if inp.is_galaxy_input_step:
                out_str += formatting.format_workflow_input(tag, inp)
        return out_str

    @property
    @abstractmethod
    def steps(self) -> list[str]:
        ...
    
    @property
    def outputs(self) -> str:
        out_str = '# OUTPUTS\n'
        for out in self.workflow.outputs:
            tag = self.workflow.tag_manager.get(out.uuid)
            out_str += formatting.format_workflow_output(tag, out)
        return out_str
        
    def init_step_text_definitions(self) -> list[StepTextDefinition]:
        step_defs: list[StepTextDefinition] = []
        step_count = 0
        for step in list(self.workflow.steps()):
            step_count += 1
            step_def = self.init_step_definition(step_count, step)
            step_defs.append(step_def)
        step_defs.sort(key=lambda x: x.step_count)
        return step_defs
    
    def init_step_definition(self, step_count: int, step: WorkflowStep) -> StepTextDefinition:
        step_definition = StepTextDefinition(
            step_count=step_count,
            step=step,
            workflow=self.workflow
        )
        return step_definition
    

    
class BulkWorkflowTextDefinition(WorkflowTextDefinition):

    def collect_workflow_imports(self) -> list[Import]:
        import_collector = WorkflowImportCollector()
        import_collector.collect_workflow_imports(self.workflow)
        for step in list(self.step_text_definitions):
            import_collector.update(step.imports)
        imports = import_collector.list_imports()
        return imports
    
    @property
    def steps(self) -> list[str]:
        """Returns actual step contents"""
        out: list[str] = ['# STEPS']
        for text_def in self.step_text_definitions:
            step_str = text_def.format_main()
            out.append(step_str)
        return out


@dataclass
class StepPage:
    tag: str
    path: str
    text: str

class StepwiseWorkflowTextDefinition(WorkflowTextDefinition):
    def __init__(self, workflow: Workflow):
        super().__init__(workflow)
        self.step_pages: list[StepPage] = self.init_step_pages()

    def init_step_pages(self) -> list[StepPage]:
        pages: list[StepPage] = []
        for text_def in self.step_text_definitions:
            step_tag = text_def.get_step_tag()
            step_dir = settings.workflow.get_janis_steps_dir()
            step_file = f'{text_def.get_step_tag()}.py'
            step_path = os.path.join(step_dir, step_file)
            page = StepPage(
                tag=step_tag,
                path=step_path,
                text=text_def.format_page()
            )
            pages.append(page)
        return pages
    
    def collect_workflow_imports(self) -> list[Import]:
        # only non-step related imports, step page imports
        import_collector = WorkflowImportCollector()
        import_collector.collect_workflow_imports(self.workflow)
        step_paths = [page.path for page in self.step_pages]
        import_collector.collect_page_imports(step_paths)
        imports = import_collector.list_imports()
        return imports
    
    @property
    def steps(self) -> list[str]:
        """Returns references to imported steps"""
        out: list[str] = ['# STEPS']
        for page in self.step_pages:
            out.append(f'# {page.tag}\n')
        return out
   


    
