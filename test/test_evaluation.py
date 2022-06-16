

import unittest

# setup imports
from data.tool_args import passing_tools
from startup.settings import load_tool_settings
from startup.ExeSettings import ToolExeSettings
from galaxy_interaction import GalaxyManager
from xmltool.load import load_xmltool, XMLToolDefinition



abricate_test_cmdlines = [
    "ln -sf 'report' report &&  abricate report  --minid=80.0 --mincov=80.0 2>&1 --db=resfinder > 'report'",
    "ln -sf 'report' report &&  abricate report  --minid=80.0 --mincov=80.0 2>&1 --db=resfinder > 'report'",
    "ln -sf 'report' report &&  abricate report --noheader --minid=80.0 --mincov=80.0 2>&1 --db=resfinder > 'report'",
    "ln -sf 'report' report &&  abricate report  --minid=80.0 --mincov=80.0 2>&1 --db=card > 'report'",
    "ln -sf 'report' report &&  abricate report  --minid=80.0 --mincov=80.0 2>&1 --db=megares > 'report'",
    "ln -sf 'report' report &&  abricate report  --minid=100.0 --mincov=80.0 2>&1 --db=resfinder > 'report'",
    "ln -sf 'report' report &&  abricate report  --minid=80.0 --mincov=100.0 2>&1 --db=resfinder > 'report'",
    "ln -sf 'report' report &&  abricate report  --minid=80.0 --mincov=80.0 2>&1 --db=resfinder > 'report'"
]


class TestToolEvaluation(unittest.TestCase):
    """
    tests the galaxy tool evaluation / templating system
    tests:
        mock objects are correctly set up
        job dict created correctly from xmltool params, inputs, outputs
        (JobFactory working as intended)
        galaxy objects like app, job, evaluator are created successfully
        output is expected from the above process
    """

    def test_evaluation(self):
        args = passing_tools['abricate']
        esettings: ToolExeSettings = load_tool_settings(args) 
        xmltool: XMLToolDefinition = load_xmltool(esettings)
        gxmanager: GalaxyManager = GalaxyManager(esettings)
        cmdlines = gxmanager.get_test_cmdstrs(xmltool)
        for cmdline in cmdlines:
            self.assertTrue(cmdline in abricate_test_cmdlines)
    
