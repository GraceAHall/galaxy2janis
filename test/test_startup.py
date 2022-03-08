



import unittest

# setup imports
from startup.settings import load_tool_settings
from startup.CLIparser import CLIparser
from startup.ExeSettings import ToolExeSettings
from runtime.exceptions import InputError


LOCAL_CLI_OK = ["gxtool2janis.py", "tool", "--dir", "test/data/abricate", "--xml", "abricate.xml"]
REMOTE_CLI_OK = ["gxtool2janis.py", "tool", "--remote_url", "https://toolshed.g2.bx.psu.edu/repos/devteam/fastqc/archive/e7b2202befea.tar.gz"]
LOCAL_CLI_USER_INPUT_FAIL1 = ["gxtool2janis.py", "tool", "--xml", "abricate.xml"]
LOCAL_CLI_USER_INPUT_FAIL2 = ["gxtool2janis.py", "--dir", "test/data/abricate", "--xml", "abricate.xml"]
LOCAL_CLI_USER_FILES_FAIL = ["gxtool2janis.py", "tool", "--dir", "test/data/abricate", "--xml", "abricates.xml"]


class TestStartup(unittest.TestCase):
    """
    test for the whole startup process
    ensures that commandline args are properly parsed & validated
    and that all files are created. 
    """

    def test_startup(self) -> None:
        # tests the complete process
        args = CLIparser(LOCAL_CLI_OK).args
        load_tool_settings(args)

    def test_startup_remote_repo(self) -> None:
        args = CLIparser(REMOTE_CLI_OK).args
        load_tool_settings(args)

    def test_startup_user_input_fail(self) -> None:
        with self.assertRaises(InputError):
            args = CLIparser(LOCAL_CLI_USER_INPUT_FAIL1).args
            load_tool_settings(args)
        with self.assertRaises(SystemExit):
            args = CLIparser(LOCAL_CLI_USER_INPUT_FAIL2).args
            load_tool_settings(args)
    
    def test_startup_user_files_fail(self) -> None:
        with self.assertRaises(Exception):
            args = CLIparser(LOCAL_CLI_USER_FILES_FAIL).args
            load_tool_settings(args)
        

    # def test_validate_xml_fails(self) -> None:
    #     """should throw FileNotFoundError"""
    #     self.validator.esettings.xmlfile = 'macros.xml'
    #     with self.assertRaises(InputException):
    #         self.validator.validate_xml()



class TestToolExeSettings(unittest.TestCase):
    """creates fake ToolExeSettings then tests some functions"""
    
    def setUp(self) -> None:
        self.args = CLIparser(LOCAL_CLI_OK).args
        self.esettings: ToolExeSettings = load_tool_settings(self.args)  

    def test_get_xml_path(self) -> None:
        true_path = 'test/data/abricate/abricate.xml'
        esettings_xml_path = self.esettings.get_xml_path()
        self.assertEquals(true_path, esettings_xml_path)
    
    def test_get_logfile_path(self) -> None:
        true_path = 'parsed/abricate/abricate.log'
        esettings_log_path = self.esettings.get_logfile_path()
        self.assertEquals(true_path, esettings_log_path)


    


