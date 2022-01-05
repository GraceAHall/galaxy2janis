

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


    def init_app(self) -> MockApp:
        app = MockApp()
        app.config.new_file_path = os.path.join(self.test_directory, "new_files")
        app.config.admin_users = "grace@thebest.com"
        app.job_search = None
        app.model.context.add(self.history)
        app.model.context.flush()
        app.config.len_file_path = "moocow"
        app.object_store = MockObjectStore()
        return app


    def init_tool(self, app: MockApp) -> GalaxyTool:
        tool_path = self.esettings.get_xml_path()
        tool_source = get_tool_source(tool_path)
        tool = create_tool_from_source(app, tool_source, config_file=tool_path)
        tool.assert_finalized()
        return tool