

import os
import tempfile

from galaxy_utils.mock import MockApp, MockObjectStore

from galaxy.tools import Tool as GalaxyToolRepresentation
from galaxy.tool_util.parser import get_tool_source
from galaxy.tools import create_tool_from_source
from galaxy.model import History


class GalaxyToolLoader:
    def __init__(self) -> None:
        self.test_directory = tempfile.mkdtemp()  
        self.history = History()
        
    def load(self, xml_path: str) -> GalaxyToolRepresentation:
        self.init_app()
        self.init_tool(xml_path)
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
        self.app.model.context.add(self.history)
        self.app.model.context.flush()

    def init_tool(self, xml_path: str) -> None:
        tool_source = get_tool_source(xml_path)
        tool = create_tool_from_source(self.app, tool_source, config_file=xml_path)
        tool.assert_finalized()
        self.tool = tool



