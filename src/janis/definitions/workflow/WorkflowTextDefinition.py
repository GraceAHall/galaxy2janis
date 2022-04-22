


from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import os

from janis.definitions.workflow.StepTextDefinition import StepTextDefinition
from startup.ExeSettings import WorkflowExeSettings
from workflows.io.WorkflowInput import WorkflowInput
from workflows.io.WorkflowOutput import WorkflowOutput
from workflows.step.WorkflowStep import WorkflowStep
from workflows.workflow.Workflow import Workflow
from janis.imports.WorkflowImportCollector import WorkflowImportCollector
import janis.definitions.workflow.snippets as snippets
#import janis.definitions.workflow.formatting as formatting
from janis.imports.Import import Import, ImportType

class WorkflowTextDefinition(ABC):
    def __init__(self, esettings: WorkflowExeSettings, workflow: Workflow):
        self.esettings = esettings
        self.workflow = workflow
        self.step_text_definitions: list[StepTextDefinition] = self.init_step_text_definitions()
    
    def init_step_text_definitions(self) -> list[StepTextDefinition]:
        step_defs: list[StepTextDefinition] = []
        step_count = 0
        for step in list(self.workflow.steps.values()):
            step_count += 1
            step_def = self.init_step_definition(step_count, step)
            step_defs.append(step_def)
        step_defs.sort(key=lambda x: x.step_count)
        return step_defs
    
    def init_step_definition(self, step_count: int, step: WorkflowStep) -> StepTextDefinition:
        import_collector = WorkflowImportCollector()
        import_collector.collect_step_imports(step, self.workflow)
        step_definition = StepTextDefinition(
            step_count=step_count,
            step=step,
            workflow=self.workflow,
            imports=import_collector.list_imports()
        )
        return step_definition
    
    @property
    def header(self) -> str:
        top_note = snippets.gxtool2janis_note_snippet(
            workflow_name=self.workflow.metadata.name,
            workflow_version=self.workflow.metadata.version
        )
        path_appends = snippets.path_append_snippet()
        return f'\n{top_note}\n\n{path_appends}\n'

    @property
    def imports(self) -> str:
        imports = self.collect_workflow_imports()
        return self.format_imports(imports)
    
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

    def format_imports(self, imports: list[Import]) -> str:
        dtype_imports = [x for x in imports if x.itype == ImportType.DATATYPE]
        class_imports = [x for x in imports if x.itype == ImportType.JANIS_CLASS]
        tool_imports = [x for x in imports if x.itype == ImportType.TOOL_DEF]
        out: str = ''
        for category in [dtype_imports, class_imports, tool_imports]:
            out += '\n'
            for imp in category:
                out += snippets.import_snippet(imp)
        out += '\n'
        return out
    
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
        comment = '# WORKFLOW DECLARATION'
        section = snippets.workflow_builder_snippet(
            tag=self.workflow.tag_manager.get(self.workflow.get_uuid()),
            version=str(self.workflow.metadata.version),
            doc=self.workflow.metadata.annotation
        )
        return f'\n{comment}\n\n{section}\n'
    
    @property
    def inputs(self) -> str:
        out_str = '# INPUTS\n'
        for inp in self.workflow.inputs:
            tag = self.workflow.tag_manager.get(inp.get_uuid())
            if inp.is_galaxy_input_step:
                out_str += snippets.workflow_input_snippet(
                    tag=tag,
                    datatype=inp.get_janis_datatype_str(),
                    doc=self.format_docstring(inp)
                )
        out_str += '\n'
        return out_str
    
    def format_docstring(self, entity: WorkflowStep | WorkflowInput | WorkflowOutput) -> Optional[str]:
        raw_doc = entity.get_docstring()
        if raw_doc:
            return raw_doc.replace('"', "'")
        return None

    @property
    @abstractmethod
    def steps(self) -> list[str]:
        ...

    @abstractmethod
    def format_step(self, textdef: StepTextDefinition) -> str:
        """
        formats a StepTextDefinition into a writable string.
        method differs between BulkWorkflowTextDefinition and StepwiseWorkflowTextDefinition
        """
        ...
    
    @property
    def outputs(self) -> str:
        out_str = '# OUTPUTS\n'
        for out in self.workflow.outputs:
            uuid = out.get_uuid()
            tag = self.workflow.tag_manager.get(uuid)
            out_str += self.format_output(tag, out)
        out_str += '\n'
        return out_str

    def format_output(self, tag: str, output: WorkflowOutput) -> str:
        return snippets.workflow_output_snippet(
            tag=tag,
            datatype=output.get_janis_datatype_str(),
            step_tag=output.step_tag,
            toolout_tag=output.toolout_tag
        )
    

    
class BulkWorkflowTextDefinition(WorkflowTextDefinition):
    
    def collect_workflow_imports(self) -> list[Import]:
        import_collector = WorkflowImportCollector()
        import_collector.collect_workflow_imports(self.workflow)
        for step in list(self.workflow.steps.values()):
            # all workflow imports
            import_collector.collect_step_imports(step, self.workflow)
        imports = import_collector.list_imports()
        return imports
    
    @property
    def steps(self) -> list[str]:
        """Returns actual step contents"""
        str_steps: list[str] = []
        for text_definition in self.step_text_definitions:
            step_str = self.format_step(text_definition)
            str_steps.append(step_str)
        return str_steps
    
    def format_step(self, textdef: StepTextDefinition) -> str:
        # subset of all StepTextDefinition properties
        out: str = ''
        out += textdef.runtime_inputs
        out += textdef.step_call
        return out




@dataclass
class StepPage:
    tag: str
    path: str
    text: str

class StepwiseWorkflowTextDefinition(WorkflowTextDefinition):
    def __init__(self, esettings: WorkflowExeSettings, workflow: Workflow):
        super().__init__(esettings, workflow)
        self.step_pages: list[StepPage] = self.init_step_pages()

    def init_step_pages(self) -> list[StepPage]:
        pages: list[StepPage] = []
        for text_def in self.step_text_definitions:
            step_tag = text_def.get_step_tag()
            step_dir = self.esettings.get_janis_steps_dir()
            step_file = f'{text_def.get_step_tag()}.py'
            step_path = os.path.join(step_dir, step_file)
            page = StepPage(
                tag=step_tag,
                path=step_path,
                text=self.format_step(text_def)
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
        out: list[str] = []
        for page in self.step_pages:
            out.append(page.tag)
        return out
   
    def format_step(self, textdef: StepTextDefinition) -> str:
        # include all StepTextDefinition properties
        out: str = ''
        out += textdef.title
        out += textdef.foreword
        out += textdef.pre_task
        out += textdef.runtime_inputs
        out += textdef.step_call
        out += textdef.post_task
        return out

    
