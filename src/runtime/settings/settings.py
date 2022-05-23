
from typing import Optional, Tuple 

from xmltool.downloads import handle_downloads

from runtime.settings.ExeSettings import ToolExeSettings, WorkflowExeSettings
from runtime.settings.SettingsInitialiser import ToolSettingsInitialiser, WorkflowSettingsInitialiser

from startup.ArgsValidator import ToolArgsValidator, WorkflowArgsValidator
from startup.FileValidator import ToolFileValidator, WorkflowFileValidator
from startup.FileInitialiser import ToolFileInitialiser, WorkflowFileInitialiser

from workflows.step.metadata.StepMetadata import StepMetadata
import utils.general_utils as utils


"""
if execution proceeds past these functions, 
all files, folders, settings etc have been validated
and managed. shouldn't be any config issues past this point. 
"""

def load_tool_settings(args: dict[str, Optional[str]], tool_id: Optional[str]=None) -> ToolExeSettings:
    ToolArgsValidator().validate(args)
    esettings = ToolSettingsInitialiser().init_settings(args)
    if esettings.remote_url and tool_id:
        esettings = handle_downloads(tool_id, esettings)
    ToolFileValidator().validate(esettings)
    ToolFileInitialiser().initialise(esettings)
    return esettings
    
def load_workflow_settings(args: dict[str, Optional[str]]) -> WorkflowExeSettings:
    WorkflowArgsValidator().validate(args)
    esettings = WorkflowSettingsInitialiser().init_settings(args)
    WorkflowFileValidator().validate(esettings)
    WorkflowFileInitialiser().initialise(esettings)
    return esettings
    
def create_tool_settings_for_step(wsettings: WorkflowExeSettings, metadata: StepMetadata) -> ToolExeSettings:
    """generates ToolExeSettings for each tool to be parsed"""
    args = _make_parse_tool_args(metadata, wsettings)
    return load_tool_settings(args, metadata.tool_id)
        
def _make_parse_tool_args(metadata: StepMetadata, esettings: WorkflowExeSettings) -> dict[str, Optional[str]]:
    if metadata.is_inbuilt:
        tool_dir, xml_filename = _get_builtin_tool_path(metadata)
        return {
            'dir': tool_dir,
            'xml': xml_filename,
            'remote_url': None,
            'download_dir': None,
            'outdir': f'{esettings.get_janis_tools_dir()}/{metadata.tool_id}',
            'cachedir': esettings.user_container_cachedir
        }
    else:
        return {
            'dir': None,
            'xml': None,
            'remote_url': metadata.get_uri(),
            'download_dir': esettings.get_xml_wrappers_dir(),
            'outdir': f'{esettings.get_janis_tools_dir()}/{metadata.tool_id}',
            'cachedir': esettings.user_container_cachedir
        }

def _get_builtin_tool_path(metadata: StepMetadata) -> Tuple[str, str]:
    import galaxy.tools
    tool_folder = str(galaxy.tools.__file__).rsplit('/', 1)[0]
    xmlfile = utils.select_xmlfile(tool_folder, metadata.tool_id)
    return tool_folder, xmlfile

