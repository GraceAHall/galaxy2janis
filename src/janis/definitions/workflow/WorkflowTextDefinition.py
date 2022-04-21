


from abc import ABC, abstractmethod
from typing import Optional
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

    @property
    def imports(self) -> str:
        imports = self.collect_workflow_imports()
        return self.format_imports(imports)
    
    @abstractmethod
    def collect_workflow_imports(self) -> list[Import]:
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
    def header(self) -> str:
        top_note = snippets.gxtool2janis_note_snippet(
            workflow_name=self.workflow.metadata.name,
            workflow_version=self.workflow.metadata.version
        )
        path_appends = snippets.path_append_snippet()
        return f'\n{top_note}\n\n{path_appends}\n'
    
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
                out_str += self.format_input(tag, inp)
        out_str += '\n'
        return out_str
    
    def format_input(self, tag: str, inp: WorkflowInput) -> str:
        return snippets.workflow_input_snippet(
            tag=tag,
            datatype=inp.get_janis_datatype_str(),
            # TODO check whether defaults and values can appear here
            doc=self.format_docstring(inp)
        )
    
    def format_docstring(self, entity: WorkflowStep | WorkflowInput | WorkflowOutput) -> Optional[str]:
        raw_doc = entity.get_docstring()
        if raw_doc:
            return raw_doc.replace('"', "'")
        return None

    @property
    def steps(self) -> list[str]:
        str_steps: list[str] = []
        step_count = 0
        for step in list(self.workflow.steps.values()):
            step_count += 1
            step_text = self.init_step_definition(step_count, step)
            step_str = self.format_step(step_text)
            str_steps.append(step_str)
        return str_steps

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

    @abstractmethod
    def format_step(self, textdef: StepTextDefinition) -> str:
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
            import_collector.collect_step_imports(step, self.workflow)
        imports = import_collector.list_imports()
        return imports
    
    def format_step(self, textdef: StepTextDefinition) -> str:
        raise NotImplementedError()



class StepwiseWorkflowTextDefinition(WorkflowTextDefinition):

    def collect_workflow_imports(self) -> list[Import]:
        import_collector = WorkflowImportCollector()
        import_collector.collect_workflow_imports(self.workflow)
        imports = import_collector.list_imports()
        return imports
    
    def format_step(self, textdef: StepTextDefinition) -> str:
        raise NotImplementedError()

    
