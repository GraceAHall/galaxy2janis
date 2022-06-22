


from runtime.exceptions import InputError
import settings.workflow.settings as settings
import fileio.validation as file_validation


def valid_workflow() -> bool:
    path = settings.workflow_path
    if file_validation.is_galaxy_workflow(path):
        return True
    return False

def validate() -> None:
    if not valid_workflow():
        raise InputError('please check workflow file path')