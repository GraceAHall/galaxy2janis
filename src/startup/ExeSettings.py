


from dataclasses import dataclass
from typing import Optional
from runtime.Logger import Logger

@dataclass
class WorkflowExeSettings:
    workflow: Optional[str] = None
    parent_outdir: Optional[str] = None
    container_cachedir: str = 'container_uri_cache.json'

    def get_workflow_path(self) -> str:
        if self.workflow:
            return self.workflow
        raise RuntimeError('cannot be called unless self.workflow has a value')
    
    def get_parent_outdir(self) -> str:
        if self.parent_outdir:
            # if set by user
            return self.parent_outdir
        else:
            # return the workflow file basename
            filepath = self.get_workflow_path()
            filepath = filepath.rsplit('/', 1)[-1].rsplit('.', 1)[0]
            filepath = filepath.replace('-', '_')
            return f'{filepath}_tools'
    
    def get_container_cache_path(self) -> str:
        return self.container_cachedir


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

        