

import unittest
from classes.execution import startup
from execution.settings import ExecutionSettings, InputWorkflow
from classes.execution.validation import InputException, SettingsValidator


class TestStartup(unittest.TestCase):
    """
    test for the whole startup process
    ensures that commandline args are properly parsed & validated
    and that all files are created. 
    """

    def setUp(self) -> None:
        self.argv = [
            "quast.xml", "test/test-data/quast", 
            "--outdir", "test/parsed",
            "--wflow", "test/test-data/assembly_qc.ga", 
            "--wstep", "3"
        ]
    
    def test_startup(self) -> None:
        # this usually returns ExecutionSettings but dont need it
        startup(self.argv) 
    
    def test_startup_fails(self) -> None:
        # this usually returns ExecutionSettings but dont need it
        self.argv = [
            "test-data/quast/quast.xml", "test/", 
        ]
        with self.assertRaises(InputException):
            startup(self.argv) 
        


class TestSettingsValidation(unittest.TestCase):
    """tests user input settings/validation"""

    def setUp(self) -> None:
        esettings = ExecutionSettings(
            'quast.xml', 
            'test/test-data/quast',
            'test/parsed'
        )        
        workflow = InputWorkflow('test/test-data/assembly_qc.ga', 3)
        esettings.workflow = workflow
        self.validator = SettingsValidator(esettings) # the important bit

    def test_validate(self) -> None:
        """
        tests the whole validation process. 
        should not raise exception
        """
        try:
            self.validator.validate()
        except:
            self.fail("validate() raised unexpected exception")
    
    def test_validate_paths(self) -> None:
        """should successfully validate filepaths and exit silently"""
        try:
            self.validator.validate_paths()
        except:
            self.fail("validate_paths() raised unexpected exception")

    def test_validate_paths_fails(self) -> None:
        """should throw InputException"""
        self.validator.esettings.xmlfile = 'quas.xml'
        with self.assertRaises(InputException):
            self.validator.validate_paths()
    
    def test_validate_xml(self) -> None:
        """should successfully validate xml and exit silently"""
        try:
            self.validator.validate_xml()
        except:
            self.fail("validate_xml() raised unexpected exception")

    def test_validate_xml_fails(self) -> None:
        """should throw InputException"""
        self.validator.esettings.xmlfile = 'macros.xml'
        with self.assertRaises(InputException):
            self.validator.validate_xml()



class TestExecutionSettings(unittest.TestCase):
    """creates fake ExecutionSettings then tests some functions"""
    
    def setUp(self) -> None:
        self.esettings = ExecutionSettings(
            'quast.xml', 
            'test/test-data/quast',
            'test/parsed'
        )        
        workflow = InputWorkflow('test/test-data/assembly_qc.ga', 3)
        self.esettings.workflow = workflow

    def test_get_xml_path(self) -> None:
        true_path = 'test/test-data/quast/quast.xml'
        esettings_xml_path = self.esettings.get_xml_path()
        self.assertEquals(true_path, esettings_xml_path)
    
    def test_get_logfile_path(self) -> None:
        true_path = 'test/parsed/quast/quast.log'
        esettings_log_path = self.esettings.get_logfile_path()
        self.assertEquals(true_path, esettings_log_path)


    


