
from typing import Any, Optional 


from runtime.settings.ExeSettings import ToolExeSettings, WorkflowExeSettings
from runtime.settings.factory import ToolSettingsInitialiser, WorkflowSettingsInitialiser

from startup.arguments import ToolArgsValidator, WorkflowArgsValidator
from startup.FileValidator import ToolFileValidator, WorkflowFileValidator
from startup.paths import ToolFileInitialiser, WorkflowFileInitialiser

from workflows.entities.step.metadata import StepMetadata


from startup.arguments import validate_workflow_args

from runtime.settings.factory import create_workflow_settings
from runtime.settings.factory import create_tool_settings

from runtime.startup.paths import setup_workfow_folder_structure
from runtime.startup.paths import setup_tool_folder_structure

from galaxy_wrappers.download import handle_downloads
from galaxy_interaction.builtin_tools import get_builtin_tool_path



"""
if execution proceeds past these functions, 
all files, folders, settings etc have been validated
and managed. shouldn't be any config issues past this point. 
"""

def load_tool_settings(args: dict[str, Optional[str]], tool_id: Optional[str]=None) -> ToolExeSettings:
    ToolArgsValidator().validate(args)
    esettings = create_tool_settings(args)
    if esettings.remote_url and tool_id:
        esettings = handle_downloads(tool_id, esettings)
    ToolFileValidator().validate(esettings)
    ToolFileInitialiser().initialise(esettings)
    return esettings
    
def load_workflow_settings(args: dict[str, Optional[str]]) -> WorkflowExeSettings:
    validate_workflow_args(args)
    esettings = create_workflow_settings(args)
    setup_workfow_folder_structure(esettings)
    return esettings
    

        

