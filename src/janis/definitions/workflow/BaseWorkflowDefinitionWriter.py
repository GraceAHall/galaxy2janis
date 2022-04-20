


from janis.imports.WorkflowImportCollector import WorkflowImportCollector
from workflows.workflow.Workflow import Workflow
from startup.ExeSettings import WorkflowExeSettings
import janis.definitions.workflow.formatting as formatting

# local
from .WorkflowDefinitionWriter import WorkflowDefinitionWriter


class BaseWorkflowDefinitionWriter(WorkflowDefinitionWriter):
    def __init__(self, esettings: WorkflowExeSettings, workflow: Workflow):
        self.esettings = esettings
        self.workflow = workflow
        self.ignore_defaults: bool = False 
        # TODO NOTE ^^^ SHOULD BE CLI RUNTIME SETTING

    def write(self) -> None:
        self.write_header()
        self.write_imports()
        self.write_metadata()
        self.write_declaration()
        self.write_inputs()
        self.write_steps()
        self.write_outputs()
    
    def write_header(self) -> None:
        top_note = formatting.format_top_note(self.workflow)
        path_appends = formatting.format_path_appends()
        self.write_to_workflow_page(top_note)
        self.write_to_workflow_page(path_appends)
    
    def write_imports(self) -> None:
        import_collector = WorkflowImportCollector()
        import_collector.collect(workflow)
        imports = import_collector.imports_to_string()
        self.write_to_workflow_page(imports)

    def write_metadata(self) -> None:
        metadata_str = formatting.format_metadata(self.workflow)
        self.write_to_workflow_page(metadata_str)
    
    def write_declaration(self) -> None:
        declaration_str = formatting.format_workflow_builder(workflow)
        self.write_to_workflow_page(declaration_str)
    
    def write_inputs(self) -> None:
        inputs_str = formatting.format_inputs(workflow)
        self.write_to_workflow_page(inputs_str)

    def write_outputs(self) -> None:
        outputs_str = formatting.format_outputs(workflow)
        self.write_to_workflow_page(outputs_str)

    def write_to_workflow_page(self, contents: str) -> None:
        filepath = self.get_workflow_page_path()
        with open(filepath, 'w') as fp:
            fp.write(contents)

    def get_workflow_page_path(self) -> str:
        return self.esettings.get_janis_workflow_path()

