

# I should probably use pathlib but dont want to bother with Path objects

import os
from typing import Optional
import xml.etree.ElementTree as et
from runtime.settings import ToolExeSettings


class InputException(Exception):
    pass


class ArgsValidator:
    def __init__(self, raw_args: dict[str, Optional[str]]) -> None:
        self.raw_args = raw_args
    
    def validate(self) -> None:
        self.validate_input_values()

    def validate_input_values(self) -> None:
        """validates user provided input settings"""
        if self.raw_args['remote_url'] is None:
            if self.raw_args['xml'] is None or self.raw_args['dir'] is None:
                raise InputException('either --remote_url or both --xml & --dir must be provided')

        if self.raw_args['xml'] and '/' in self.raw_args['xml']:
            raise InputException('xml is the xml file name. cannot include "/".')
            

class FileValidator:
    def __init__(self, esettings: ToolExeSettings) -> None:
        self.esettings = esettings

    def validate(self) -> None:
        """validates input, output, and runtime files"""
        self.validate_paths()
        self.validate_xml()
        # future: validate_workflow()

    def validate_paths(self) -> None:
        """checks that all necessary input files exist"""
        validation_files = self.get_validation_files()
        for filepath in validation_files:
            if not os.path.exists(filepath):
                raise InputException(f'file does not exist: {filepath}')

    def get_validation_files(self) -> list[str]:
        es = self.esettings
        validation_files = [
            es.get_xml_path(),
        ]
        return [f for f in validation_files if type(f) is str]

    def validate_xml(self) -> None:
        """checks that the provided xml is tool xml"""
        tree = et.parse(self.esettings.get_xml_path())
        root = tree.getroot()
        if root.tag != 'tool':
            raise InputException(f'{self.esettings.get_xml_path()} is not tool xml')