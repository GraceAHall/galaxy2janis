
from typing import Optional
from startup.ExeSettings import ToolExeSettings, WorkflowExeSettings
from startup.ArgsValidator import ToolArgsValidator, WorkflowArgsValidator
from startup.SettingsInitialiser import ToolSettingsInitialiser, WorkflowSettingsInitialiser
from startup.downloads import handle_downloads
from startup.FileValidator import ToolFileValidator, WorkflowFileValidator
from startup.FileInitialiser import ToolFileInitialiser, WorkflowFileInitialiser



"""
if execution proceeds past these functions, 
all files, folders, settings etc have been validated
and managed. shouldn't be any config issues past this point. 
"""


def load_tool_settings(args: dict[str, Optional[str]], intended_tool_id: Optional[str]=None) -> ToolExeSettings:
    ToolArgsValidator().validate(args)
    esettings = ToolSettingsInitialiser().init_settings(args)
    if esettings.remote_url and intended_tool_id:
        esettings = handle_downloads(intended_tool_id, esettings)
    ToolFileValidator().validate(esettings)
    ToolFileInitialiser().initialise(esettings)
    return esettings
    
def load_workflow_settings(args: dict[str, Optional[str]]) -> WorkflowExeSettings:
    WorkflowArgsValidator().validate(args)
    esettings = WorkflowSettingsInitialiser().init_settings(args)
    WorkflowFileValidator().validate(esettings)
    WorkflowFileInitialiser().initialise(esettings)
    return esettings
    
    
