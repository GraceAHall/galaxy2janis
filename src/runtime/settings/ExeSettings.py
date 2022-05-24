


from dataclasses import dataclass
from typing import Optional

@dataclass
class WorkflowExeSettings:
    workflow: str
    outdir: str
    container_cachedir: str

    def get_container_cache_path(self) -> str:
        return self.container_cachedir
        
    def get_logfile_path(self) -> str:
        return f'{self.outdir}/workflow.log'


    def get_janis_workflow_path(self) -> str:
        return f'{self.outdir}/workflow.py'
    
    def get_janis_workflow_configfile_path(self) -> str:
        return f'{self.outdir}/config.py'

    def get_xml_wrappers_dir(self) -> str:
        return f'{self.outdir}/wrappers'
    
    def get_janis_tools_dir(self) -> str:
        return f'{self.outdir}/tools'

    def get_janis_steps_dir(self) -> str:
        return f'{self.outdir}/steps'



@dataclass
class ToolExeSettings:
    download_dir: str
    container_cachedir: str
    xmlfile: Optional[str] = None
    xmldir: Optional[str] = None
    remote_url: Optional[str] = None
    user_outdir: Optional[str] = None

    def get_xml_path(self) -> str:
        """joins the xmldir and xmlfile to provide xml path"""
        if self.xmldir and self.xmlfile:
            return f'{self.xmldir}/{self.xmlfile}'
        raise RuntimeError('cannot be called until xmldir and xmlfile are set.')            
    
    def get_outdir(self) -> str:
        if self.user_outdir:
            return self.user_outdir
        elif self.xmlfile:
            basename = self.xmlfile.lower().replace('-', '_').rsplit('.', 1)[0]
            return f'parsed/tools/{basename}'
        else:
            raise RuntimeError('cannot be called until xmlfile is set.')            

    def get_logfile_path(self) -> str:
        if self.xmlfile:
            toolname = self.xmlfile.rsplit('.', 1)[0]
            return f'{self.get_outdir()}/{toolname}.log'
        raise RuntimeError('cannot be called until xmlfile is set.')            
    
    def get_janis_definition_path(self) -> str:
        if self.xmlfile:
            toolname = self.xmlfile.rsplit('.', 1)[0]
            return f'{self.get_outdir()}/{toolname}.py'
        raise RuntimeError('cannot be called until xmlfile is set.')            


        