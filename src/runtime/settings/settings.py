
from typing import Any, Optional, Tuple 
import os 

from xmltool.downloads import handle_downloads

from runtime.settings.ExeSettings import ToolExeSettings, WorkflowExeSettings
from runtime.settings.SettingsInitialiser import ToolSettingsInitialiser, WorkflowSettingsInitialiser

from startup.ArgsValidator import ToolArgsValidator, WorkflowArgsValidator
from startup.FileValidator import ToolFileValidator, WorkflowFileValidator
from startup.FileInitialiser import ToolFileInitialiser, WorkflowFileInitialiser

from workflows.entities.step.metadata import StepMetadata
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
    ToolFileInitialiser(esettings).initialise()
    return esettings
    
def load_workflow_settings(args: dict[str, Optional[str]]) -> WorkflowExeSettings:
    WorkflowArgsValidator().validate(args)
    esettings = WorkflowSettingsInitialiser().init_settings(args)
    WorkflowFileValidator().validate(esettings)
    WorkflowFileInitialiser(esettings).initialise()
    return esettings
    
def create_tool_settings_for_step(wsettings: WorkflowExeSettings, metadata: StepMetadata) -> ToolExeSettings:
    """generates ToolExeSettings for each tool to be parsed"""
    args = _make_parse_tool_args(metadata, wsettings)
    return load_tool_settings(args, metadata.tool_id)
        
def _make_parse_tool_args(metadata: StepMetadata, wsettings: WorkflowExeSettings) -> dict[str, Any]:
    if metadata.is_inbuilt:
        tool_dir, xml_filename = _get_builtin_tool_path(metadata)
        return {
            'dir': tool_dir,
            'xml': xml_filename,
            'remote_url': None,
            'download_dir': None,
            'outdir': f'{wsettings.get_janis_tools_dir()}/{metadata.tool_id}',
            'cachedir': wsettings.container_cachedir,
            'dev_no_test_cmdstrs': wsettings.dev_no_test_cmdstrs
        }
    else:
        return {
            'dir': None,
            'xml': None,
            'remote_url': metadata.get_url(),
            'download_dir': wsettings.get_xml_wrappers_dir(),
            'outdir': f'{wsettings.get_janis_tools_dir()}/{metadata.tool_id}',
            'cachedir': wsettings.container_cachedir,
            'dev_no_test_cmdstrs': wsettings.dev_no_test_cmdstrs
        }

def _get_builtin_tool_path(metadata: StepMetadata) -> Tuple[str, str]:
    tool_directories = _get_builtin_tool_directories()
    for directory in tool_directories:
        xmlfile = utils.get_xmlfile_by_tool_id(directory, metadata.tool_id)
        if xmlfile:
            return directory, xmlfile
    raise RuntimeError(f'cannot locate builtin tool {metadata.tool_id}') 

def _get_builtin_tool_directories() -> list[str]:
    out: list[str] = []
    out += _get_builtin_tools_directories()
    out += _get_datatype_converter_directories()
    return out

def _get_builtin_tools_directories() -> list[str]:
    import galaxy.tools
    tools_folder = str(galaxy.tools.__file__).rsplit('/', 1)[0]
    bundled_folders = os.listdir(f'{tools_folder}/bundled')
    bundled_folders = [f for f in bundled_folders if not f.startswith('__')]
    bundled_folders = [f'{tools_folder}/bundled/{f}' for f in bundled_folders]
    bundled_folders = [f for f in bundled_folders if os.path.isdir(f)]
    return [tools_folder] + bundled_folders

def _get_datatype_converter_directories() -> list[str]:
    import galaxy.datatypes
    datatypes_folder = str(galaxy.datatypes.__file__).rsplit('/', 1)[0]
    converters_folder = f'{datatypes_folder}/converters'
    return [converters_folder]
