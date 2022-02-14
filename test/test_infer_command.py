

import unittest

from gxtool2janis import load_galaxy_manager, load_tool, infer_command
from runtime.startup import load_settings
from runtime.settings import ExecutionSettings


class TestCommandInference(unittest.TestCase):
    """tests whether a Command() is correctly generated"""

    def setUp(self) -> None:
        argv = [
            "abricate.xml", "test/data/abricate", 
            "--outdir", "test/rubbish",
        ]
        esettings: ExecutionSettings = load_settings(argv)
        gxmanager = load_galaxy_manager(esettings)
        self.tool = load_tool(gxmanager)
        self.command = infer_command(gxmanager, self.tool)

    def test_command_statements(self) -> None:
        pass

    def test_tool_statement(self) -> None:
        pass


