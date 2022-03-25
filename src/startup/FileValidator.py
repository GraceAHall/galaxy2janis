

import os
import xml.etree.ElementTree as et
from startup.ExeSettings import ToolExeSettings, WorkflowExeSettings
from runtime.exceptions import InputError


class WorkflowFileValidator:

    def validate(self, esettings: WorkflowExeSettings) -> None:
        self.esettings = esettings

    def validate_paths(self) -> None:
        """checks that all necessary input files exist"""
        validation_files = self.get_validation_files()
        for filepath in validation_files:
            if not os.path.exists(filepath):
                raise InputError(f'file does not exist: {filepath}')

    def get_validation_files(self) -> list[str]:
        validation_files = [
            self.esettings.get_galaxy_workflow_path(),
        ]
        return [f for f in validation_files if type(f) is str]


class ToolFileValidator:
    
    def validate(self, esettings: ToolExeSettings) -> None:
        """validates input, output, and runtime files"""
        self.esettings = esettings
        self.validate_paths()

    def validate_paths(self) -> None:
        """checks that all necessary input files exist"""
        validation_files = self.get_validation_files()
        for filepath in validation_files:
            if not os.path.exists(filepath):
                raise InputError(f'file does not exist: {filepath}')

    def get_validation_files(self) -> list[str]:
        validation_files = [
            self.esettings.get_xml_path(),
        ]
        return [f for f in validation_files if type(f) is str]

    def validate_xml(self) -> None:
        """checks that the provided xml is tool xml"""
        tree = et.parse(self.esettings.get_xml_path())
        root = tree.getroot()
        if root.tag != 'tool':
            raise InputError(f'{self.esettings.get_xml_path()} is not tool xml')