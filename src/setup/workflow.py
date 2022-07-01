


import settings

from typing import Any

def workflow_setup(args: dict[str, Any]) -> None:
    update_workflow_settings(args)
    settings.validation.validate_workflow_settings()

def update_workflow_settings(args: dict[str, Any]) -> None:
    raise NotImplementedError()

