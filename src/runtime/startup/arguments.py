


from abc import ABC, abstractmethod
from typing import Optional
from runtime.exceptions import InputError


def validate_workflow_args(raw_args: dict[str, Optional[str]]) -> None:
    validator = WorkflowArgsValidator(raw_args)
    validator.validate()

def validate_tool_args(raw_args: dict[str, Optional[str]]) -> None:
    validator = ToolArgsValidator(raw_args)
    validator.validate()


class ArgsValidator(ABC):
    def __init__(self, raw_args: dict[str, Optional[str]]):
        self.args = raw_args
    
    @abstractmethod
    def validate(self) -> None:
        ...


class WorkflowArgsValidator(ArgsValidator):

    def validate(self) -> None:
        self.validate_input_values()

    def validate_input_values(self) -> None:
        """validates user provided input settings"""
        if self.args['workflow'] is None:
            raise InputError('workflow must be provided.')


class ToolArgsValidator(ArgsValidator):
    
    def validate(self) -> None:
        self.validate_input_values()

    def validate_input_values(self) -> None:
        """validates user provided input settings"""
        if self.args['remote_url'] is None:
            if self.args['xml'] is None or self.args['dir'] is None:
                raise InputError('either --remote_url or both --xml & --dir must be provided')

        if self.args['xml'] and '/' in self.args['xml']:
            raise InputError('xml is the xml file name. cannot include "/".')