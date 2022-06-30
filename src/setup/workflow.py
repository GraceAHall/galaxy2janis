


import settings
import logs.logging as logging

from typing import Any

def do_workflow_setup(args: dict[str, Any]) -> None:
    update_workflow_settings(args)
    settings.validation.validate_workflow_settings()
    setup_file_structure()
    update_logging()

def update_workflow_settings(args: dict[str, Any]) -> None:
    raise NotImplementedError()

def setup_file_structure() -> None:
    raise NotImplementedError()

def update_logging() -> None:
    logging.configure_workflow_logging()
    logging.msg_parsing_workflow()