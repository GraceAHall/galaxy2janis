

import os
import tempfile
from classes.execution.settings import ExecutionSettings

from galaxy.tools import Tool as GalaxyTool
from galaxy.tool_util.parser import get_tool_source
from galaxy.tools import create_tool_from_source
from classes.templating.MockClasses import MockApp, MockObjectStore
from galaxy.model import History


class GalaxyLoader:
    def __init__(self, esettings: ExecutionSettings) -> None:
        self.esettings = esettings
        self.test_directory = tempfile.mkdtemp()  
        self.history = History()
        
    def load(self) -> GalaxyTool:
        self.init_app()
        self.init_tool()
        return self.tool

    def init_app(self) -> None:
        self.app = MockApp()
        self.update_app()
        self.update_app_config()
        self.update_app_database()

    def update_app(self) -> None:
        self.app.job_search = None
        self.app.object_store = MockObjectStore()

    def update_app_config(self) -> None:
        self.app.config.new_file_path = os.path.join(self.test_directory, "new_files")
        self.app.config.admin_users = "grace@thebest.com"
        self.app.config.len_file_path = "moocow"

    def update_app_database(self) -> None:
        app.model.context.add(self.history)
        app.model.context.flush()

    def init_tool(self) -> GalaxyTool:
        tool_path = self.esettings.get_xml_path()
        tool_source = get_tool_source(tool_path)
        tool = create_tool_from_source(self.app, tool_source, config_file=tool_path)
        tool.assert_finalized()
        self.tool = tool
