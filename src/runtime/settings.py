


from dataclasses import dataclass
from typing import Optional

@dataclass
class InputWorkflow:
    path: str
    step: int

@dataclass
class WorkflowExeSettings:
    pass

@dataclass
class ToolExeSettings:
    xmlfile: Optional[str] = None
    xmldir: Optional[str] = None
    remote_url: Optional[str] = None
    parent_outdir: str = 'parsed'
    container_cachedir: str = 'container_uri_cache.json'

    def get_xml_path(self) -> str:
        """joins the xmldir and xmlfile to provide xml path"""
        if self.xmldir and self.xmlfile:
            return f'{self.xmldir}/{self.xmlfile}'
        raise RuntimeError('cannot be called until xmldir and xmlfile are set.')            

    def get_tool_test_dir(self) -> str:
        if self.xmldir:
            return f'{self.xmldir}/test-data'
        raise RuntimeError('cannot be called until xmldir is set.')            

    def get_outdir(self) -> str:
        """
        gets the path to the runtime outdir.
        contains logs and parsed janis tool definition
        """
        if self.xmldir:
            parent_folder = self.parent_outdir + '/'
            folder = self.xmldir.rsplit('/', 1)[-1]
            return parent_folder + folder
        raise RuntimeError('cannot be called until xmldir and xmlfile are set.')            

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

    def get_container_cache_path(self) -> str:
        return self.container_cachedir

    def get_datatype_definitions_path(self) -> str:
        return 'datatypes/gxformat_combined_types.yaml' # TODO make this an actual CLI setting

        