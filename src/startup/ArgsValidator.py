


from typing import Optional
from runtime.exceptions import InputError


class WorkflowArgsValidator:

    def validate(self, raw_args: dict[str, Optional[str]]) -> None:
        self.validate_input_values(raw_args)

    def validate_input_values(self, raw_args: dict[str, Optional[str]]) -> None:
        """validates user provided input settings"""
        if raw_args['workflow'] is None:
            raise InputError('workflow must be provided.')


class ToolArgsValidator:
    
    def validate(self, raw_args: dict[str, Optional[str]]) -> None:
        self.validate_input_values(raw_args)

    def validate_input_values(self, raw_args: dict[str, Optional[str]]) -> None:
        """validates user provided input settings"""
        if raw_args['remote_url'] is None:
            if raw_args['xml'] is None or raw_args['dir'] is None:
                raise InputError('either --remote_url or both --xml & --dir must be provided')

        if raw_args['xml'] and '/' in raw_args['xml']:
            raise InputError('xml is the xml file name. cannot include "/".')