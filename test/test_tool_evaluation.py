


import unittest

from gxtool2janis import load_galaxy_manager, load_tool
from runtime.startup import load_settings
from runtime.settings import ExecutionSettings



class TestToolEvaluation(unittest.TestCase):
    """
    tests the galaxy tool evaluation / templating system
    tests:
        mock objects are correctly set up
        job dict created correctly from tool params, inputs, outputs
        (JobFactory working as intended)
        galaxy objects like app, job, evaluator are created successfully
        output is expected from the above process
    """

    def setUp(self) -> None:
        argv = [
            "abricate.xml", "test/data/abricate", 
            "--outdir", "test/rubbish",
        ]
        esettings: ExecutionSettings = load_settings(argv)
        self.gxmanager = load_galaxy_manager(esettings)
        self.tool = load_tool(self.gxmanager)
        
    def test_evaluation(self):
        TEMPLATED_STR = "ln -sf '__ʕ•́ᴥ•̀ʔっ♡_file_input' file_input &&  abricate file_input  --minid=80.0 --mincov=80.0 --db=resfinder > '__ʕ•́ᴥ•̀ʔっ♡_report'"

        cmdstrs = self.gxmanager.get_raw_cmdstrs(self.tool)
        test_cmd_strs = [cstr[1] for cstr in cmdstrs if cstr[0] == 'test']
        self.assertEquals(len(test_cmd_strs), 8)
        self.assertEquals(test_cmd_strs[0], TEMPLATED_STR)
        