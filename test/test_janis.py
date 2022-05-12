


import unittest
import os

from mock.mock_esettings import MOCK_TOOL_ESETTINGS
from mock.mock_xmltool import MOCK_XMLTOOL
from mock.mock_command import MOCK_COMMAND
from mock.mock_container import MOCK_CONTAINER

from file_io.write import write_tool
from tool.generate import gen_tool


# NOTE THIS IS LAZY
# relies on ToolFactory working correctly to create our mock Tool.
# ideally I would write out the mock Tool, but that takes time. 

class TestJanisFormatting(unittest.TestCase):

    def setUp(self) -> None:
        if not os.path.exists(MOCK_TOOL_ESETTINGS.get_outdir()):
            os.mkdir(MOCK_TOOL_ESETTINGS.get_outdir())
        self.tool = gen_tool(
            xmltool=MOCK_XMLTOOL,
            command=MOCK_COMMAND,
            container=MOCK_CONTAINER,
        )
        write_tool(
            esettings=MOCK_TOOL_ESETTINGS,
            tool=self.tool
        )

    def test_formatting(self) -> None:
        with open(MOCK_TOOL_ESETTINGS.get_janis_definition_path(), 'r') as fp:
            this_definition = fp.readlines()
        with open('test/data/reference/abricate.py', 'r') as fp:
            reference_definition = fp.readlines()
      
        for line in this_definition:
            self.assertIn(line, reference_definition)


