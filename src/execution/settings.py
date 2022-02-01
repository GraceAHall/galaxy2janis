


from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

class RunMode(Enum):
    DEFAULT = auto()
    DEBUG = auto()

@dataclass
class InputWorkflow:
    path: str
    step: int

@dataclass
class ExecutionSettings:
    xmlfile: str
    xmldir: str
    parent_outdir: Optional[str] = None
    workflow: Optional[InputWorkflow] = None
    runmode: RunMode = RunMode.DEFAULT

    def get_xml_path(self) -> str:
        """joins the xmldir and xmlfile to provide xml path"""
        return f'{self.xmldir}/{self.xmlfile}'

    def get_outdir(self) -> str:
        """
        gets the path to the runtime outdir.
        contains logs and parsed janis tool definition
        """
        parent_folder = self.parent_outdir + '/' if self.parent_outdir else ''
        folder = self.xmldir.rsplit('/', 1)[-1]
        return parent_folder + folder

    def get_logfile_path(self) -> str:
        toolname = self.xmlfile.rsplit('.', 1)[0]
        return f'{self.get_outdir()}/{toolname}.log'
    
    def get_janis_definition_path(self) -> str:
        toolname = self.xmlfile.rsplit('.', 1)[0]
        return f'{self.get_outdir()}/{toolname}.py'

    def add_workflow(self, workflow: InputWorkflow) -> None:
        """adds a workflow object to settings"""
        self.workflow = workflow  

    def get_workflow_path(self) -> Optional[str]:
        """gets the relative path to the provided workflow file"""
        if self.workflow:
            return self.workflow.path

    def get_workflow_step(self) -> Optional[int]:
        """gets the workflow step we will parse"""
        if self.workflow:
            return self.workflow.step


