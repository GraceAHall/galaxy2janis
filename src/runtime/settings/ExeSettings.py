


from dataclasses import dataclass
from typing import Optional

from file_io.formats.paths import PathManager


@dataclass
class WorkflowExeSettings:
    workflow_path: str 
    container_cache_path: str
    dev_no_test_cmdstrs: bool
    dev_no_partial_eval: bool
    outpaths: PathManager


@dataclass
class ToolExeSettings:
    download_dir: str
    container_cachedir: str
    dev_no_test_cmdstrs: bool
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


        