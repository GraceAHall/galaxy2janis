
from runtime.exceptions import InputError
import settings.tool.settings as settings
import fileio.validation as file_validation


def local_mode() -> bool:
    if settings.tool_path:
        return True
    return False

def remote_mode() -> bool:
    if settings.owner and settings.repo and settings.revision:
        return True
    return False

def valid_xml() -> bool:
    path = settings.tool_path
    if file_validation.is_tool_xml(path):
        return True
    return False

def validate_tool_settings() -> None:
    if not local_mode() and not remote_mode():
        raise InputError('please supply either --local or --remote')
    if local_mode() and not valid_xml():
        raise InputError('please check xml file path')




