



import os
import tempfile
from typing import Optional

from galaxy.tools import Tool as GxTool
from galaxy.tool_util.parser import get_tool_source
from galaxy.tools import create_tool_from_source
from galaxy.model import History

from gxmanager.mock import MockApp, MockObjectStore
from tool.tool_definition import GalaxyToolDefinition

from gxmanager.cmdstrings.test_commands.TestCommandLoader import TestCommandLoader
from gxmanager.cmdstrings.xml_commands.XMLCommandLoader import XMLCommandLoader

from command.CommandString import CommandString


class GalaxyManager:
    def __init__(self, xml_path: str) -> None:
        self.xml_path = xml_path
        self.history = History()
        self.app: Optional[MockApp] = None
        self.tool: Optional[GxTool] = None

    def get_app(self) -> MockApp:
        if self.app:
            return self.app
        else:
            self.app = self._init_app()
        return self.app

    def get_tool(self) -> GxTool:
        if self.tool:
            return self.tool
        else:
            self.tool = self._init_tool()
        return self.tool

    def get_command_strings(self, tooldef: GalaxyToolDefinition) -> list[CommandString]:
        test_cmds = self._get_test_commands(tooldef)
        xml_cmd = self._get_xml_command(tooldef)
        #workflow_cmd = self._get_workflow_command()
        return test_cmds + [xml_cmd]
    
    def _get_test_commands(self, tooldef: GalaxyToolDefinition) -> list[CommandString]:
        app = self.get_app()
        gxtool = self.get_tool()
        tcl = TestCommandLoader(app, self.history, gxtool, tooldef)
        cmdstrs = [tcl.load(test) for test in gxtool.tests]
        cmdstrs = [s for s in cmdstrs if s is not None]
        return cmdstrs

    def _get_xml_command(self, tooldef: GalaxyToolDefinition) -> list[str]:
        # create CommandString for tooldef.command
        xcl = XMLCommandLoader(tooldef)
        return xcl.load()

    def _get_workflow_command(self) -> None:
        raise NotImplementedError
        
    def _init_app(self) -> MockApp:
        # basic details
        app = MockApp()
        app.job_search = None
        app.object_store = MockObjectStore()
        # config
        app.config.new_file_path = os.path.join(tempfile.mkdtemp(), "new_files")
        app.config.admin_users = "grace@thebest.com"
        app.config.len_file_path = "moocow"
        # database
        app.model.context.add(self.history)
        app.model.context.flush()
        return app

    def _init_tool(self) -> GxTool:
        app = self.get_app()
        tool_source = get_tool_source(self.xml_path)
        tool = create_tool_from_source(app, tool_source, config_file=self.xml_path)
        tool.assert_finalized()
        return tool


