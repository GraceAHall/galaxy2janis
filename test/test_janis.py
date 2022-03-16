


import unittest
import os

from mock.mock_esettings import MOCK_ESETTINGS
from mock.mock_tool import MOCK_TOOL
from mock.mock_command import MOCK_COMMAND
from mock.mock_container import MOCK_CONTAINER

from janis.write_definition import write_janis

class TestJanisFormatting(unittest.TestCase):

    def test_formatting(self) -> None:
        if not os.path.exists(MOCK_ESETTINGS.get_outdir()):
            os.mkdir(MOCK_ESETTINGS.get_outdir())
        write_janis(
            MOCK_ESETTINGS,
            MOCK_TOOL,
            MOCK_COMMAND,
            MOCK_CONTAINER
        )
        with open(MOCK_ESETTINGS.get_janis_definition_path(), 'r') as fp:
            this_definition = fp.readlines()
        with open('test/data/reference/abricate.py', 'r') as fp:
            reference_definition = fp.readlines()
      
        for line in this_definition:
            self.assertIn(line, reference_definition)


