

from galaxy2janis.logs import logging
from galaxy2janis import settings

from typing import Any
from galaxy2janis.runtime.exceptions import InputError
from galaxy2janis.utils import galaxy as utils


def workflow_setup(args: dict[str, Any]) -> None:
    settings.workflow.set_path(args['infile'])
    settings.workflow.set_dev_partial_eval(args['dev_partial_eval'])
    logging.msg_parsing_workflow()
    validate_workflow_settings()

### VALIDATION ###

def validate_workflow_settings() -> None:
    if not _valid_workflow():
        raise InputError('please check workflow file path')

def _valid_workflow() -> bool:
    path = settings.workflow.workflow_path
    if utils.is_galaxy_workflow(path):
        return True
    return False

