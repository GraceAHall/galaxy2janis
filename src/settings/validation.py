
import settings

from runtime.exceptions import InputError
import utils.galaxy as utils


### TOOL ###

def _local_mode() -> bool:
    if settings.tool.tool_path:
        return True
    return False

def _remote_mode() -> bool:
    if settings.tool.owner and settings.tool.repo and settings.tool.revision:
        return True
    return False

def _valid_xml() -> bool:
    path = settings.tool.tool_path
    if utils.is_tool_xml(path):
        return True
    return False


def validate_tool_settings() -> None:
    # both local & remote params not given
    if not _local_mode() and not _remote_mode():
        raise InputError('please supply either --local or --remote')
    
    # local params but not valid xml
    if _local_mode() and not _valid_xml():
        raise InputError('please check xml file path')



### WORKFLOW ###

def _valid_workflow() -> bool:
    path = settings.workflow.workflow_path
    if utils.is_galaxy_workflow(path):
        return True
    return False

def validate_workflow_settings() -> None:
    if not _valid_workflow():
        raise InputError('please check workflow file path')