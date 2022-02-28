
import os
from typing import Optional
from startup.ExeSettings import ToolExeSettings, WorkflowExeSettings
from startup.ArgsValidator import ToolArgsValidator, WorkflowArgsValidator
from startup.SettingsInitialiser import ToolSettingsInitialiser, WorkflowSettingsInitialiser
from startup.downloads import download_repo
from startup.FileValidator import ToolFileValidator, WorkflowFileValidator
from startup.FileInitialiser import ToolFileInitialiser, WorkflowFileInitialiser



"""
if execution proceeds past these functions, 
all files, folders, settings etc have been validated
and managed. shouldn't be any config issues past this point. 
"""


def load_tool_settings(args: dict[str, Optional[str]]) -> ToolExeSettings:
    ToolArgsValidator().validate(args)
    settings = ToolSettingsInitialiser().init_settings(args)
    settings = handle_downloads(settings)
    ToolFileValidator().validate(settings)
    ToolFileInitialiser().initialise(settings)
    return settings

def handle_downloads(esettings: ToolExeSettings) -> ToolExeSettings:
    if esettings.remote_url:
        folder = download_repo(esettings.remote_url, esettings.parent_outdir)
        esettings.xmldir = folder
        xmls = [x for x in os.listdir(folder) if x.endswith('.xml') and 'macros' not in x]
        esettings.xmlfile = xmls[0]
    return esettings
    
def load_workflow_settings(args: dict[str, Optional[str]]) -> WorkflowExeSettings:
    WorkflowArgsValidator().validate(args)
    settings = WorkflowSettingsInitialiser().init_settings(args)
    WorkflowFileValidator().validate(settings)
    WorkflowFileInitialiser().initialise(settings)
    return settings
    
    
