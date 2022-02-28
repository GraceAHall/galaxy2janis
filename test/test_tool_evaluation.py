

import unittest
from data.tool_args import error_tools, passing_tools

from startup.settings import load_settings, ToolExeSettings
from galaxy_interaction import load_manager, GalaxyManager
from tool.load import load_tool, GalaxyToolDefinition


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
        args: list[str] = passing_tools['abricate']
        esettings: ToolExeSettings = load_settings(args)
        self.gxmanager: GalaxyManager = load_manager(esettings)
        self.tool: GalaxyToolDefinition = load_tool(self.gxmanager)
        
    def test_evaluation(self):
        TEMPLATED_STR = "ln -sf '__ʕ•́ᴥ•̀ʔっ♡_file_input' file_input &&  abricate file_input  --minid=80.0 --mincov=80.0 --db=resfinder > '__ʕ•́ᴥ•̀ʔっ♡_report'"

        cmdstrs = self.gxmanager.get_raw_cmdstrs(self.tool)
        test_cmd_strs = [cstr[1] for cstr in cmdstrs if cstr[0] == 'test']
        self.assertEquals(len(test_cmd_strs), 8)
        self.assertEquals(test_cmd_strs[0], TEMPLATED_STR)
        