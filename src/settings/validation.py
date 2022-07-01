
import settings

from runtime.exceptions import InputError
import utils.galaxy as utils


### TOOL ###

def _has_xml() -> bool:
    if settings.tool.tool_path:
        return True
    return False

def _valid_xml() -> bool:
    path = settings.tool.tool_path
    if utils.is_tool_xml(path):
        return True
    return False

def validate_tool_settings() -> None:
    # both local & remote params not given
    if not _has_xml() or not _valid_xml():
        raise RuntimeError('no valid xml file')


### WORKFLOW ###

def _valid_workflow() -> bool:
    path = settings.workflow.workflow_path
    if utils.is_galaxy_workflow(path):
        return True
    return False

def validate_workflow_settings() -> None:
    if not _valid_workflow():
        raise InputError('please check workflow file path')