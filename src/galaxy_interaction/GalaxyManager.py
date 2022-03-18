

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from xmltool.tool_definition import XMLToolDefinition

import os
import tempfile
import packaging.version

from typing import Optional

from galaxy.tools import Tool as GxTool
from galaxy.tool_util.parser import get_tool_source
from galaxy.tools import create_tool_from_source
from galaxy.model import History

from galaxy_interaction.mock import MockApp, MockObjectStore
from startup.ExeSettings import ToolExeSettings

from galaxy_interaction.cmdstrings.loaders.TestCommandLoader import TestCommandLoader
from galaxy_interaction.cmdstrings.loaders.XMLCommandLoader import XMLCommandLoader



class GalaxyManager:
    def __init__(self, esettings: ToolExeSettings):
        """ 
        Manages all galaxy related operations.
        This includes loading tool xml, templating test cases into command strings, 
        creating galaxy app etc

        Ideally, all galaxy operations are contained within this class. 
        
        single history needed during execution, otherwise will have to reload app 
        (don't know how to dynamically swap histories using the api) 
        """
        self.esettings = esettings
        self.history = History()  
        self.app: Optional[MockApp] = None
        self.gxtool: Optional[GxTool] = None

    def get_app(self) -> MockApp:
        if self.app:
            return self.app
        else:
            self.app = self._init_app()
        return self.app

    def get_tool(self) -> GxTool:
        if self.gxtool:
            return self.gxtool
        else:
            self.gxtool = self._init_tool()
        return self.gxtool

    # def get_raw_cmdstrs(self, tooldef: XMLToolDefinition) -> list[Tuple[str, str]]:
    #     test_cmds = self._get_test_commands(tooldef)
    #     xml_cmds = self._get_xml_commands(tooldef)
    #     #workflow_cmds = self._get_workflow_command()

    #     out: list[Tuple[str, str]] = []
    #     out += [('xml', cmdstr) for cmdstr in xml_cmds]
    #     out += [('test', cmdstr) for cmdstr in test_cmds]
    #     #out += [('workflow', cmdstr) for cmdstr in workflow_cmds]
    #     return out

    def get_test_cmdstrs(self, tooldef: XMLToolDefinition) -> list[str]:
        app = self.get_app()
        gxtool = self.get_tool()
        tcl = TestCommandLoader(app, self.history, gxtool, tooldef, self.esettings)
        test_cmdstrs = [tcl.load(test) for test in gxtool.tests]
        valid_cmdstrs = [s for s in test_cmdstrs if s is not None]
        return valid_cmdstrs

    def get_xml_cmdstr(self, tooldef: XMLToolDefinition) -> str:
        # create DynamicCommandString for tooldef.command
        xcl = XMLCommandLoader(tooldef)
        return xcl.load()

    def get_workflow_cmdstr(self, tooldef: XMLToolDefinition) -> str:
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
        tool_source = get_tool_source(self.esettings.get_xml_path())
        tool = create_tool_from_source(app, tool_source)
        tool.assert_finalized()
        return tool


