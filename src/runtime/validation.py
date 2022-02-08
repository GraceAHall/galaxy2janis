


# from pathlib import Path
# I should probably use pathlib but dont want to bother with Path objects

import os
import xml.etree.ElementTree as et

from runtime.settings import ExecutionSettings


class InputException(Exception):
    pass


class SettingsValidator:
    def __init__(self, esettings: ExecutionSettings) -> None:
        self.esettings = esettings
    
    def validate(self) -> None:
        self.validate_input_values()
        self.validate_files()

    def validate_input_values(self) -> None:
        """validates all user provided input settings"""
        if '/' in self.esettings.xmlfile:
            raise InputException('xmlfile is the xml file name. cannot include "/".')
            
    def validate_files(self) -> None:
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
            es.get_workflow_path()
        ]
        return [f for f in validation_files if type(f) is str]

    def validate_xml(self) -> None:
        """checks that the provided xml is tool xml"""
        tree = et.parse(self.esettings.get_xml_path())
        root = tree.getroot()
        if root.tag != 'tool':
            raise InputException(f'{self.esettings.get_xml_path()} is not tool xml')