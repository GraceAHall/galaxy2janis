



from runtime.Logger import Logger

from typing import Optional

from startup.settings import load_tool_settings
from startup.ExeSettings import ToolExeSettings
from galaxy_interaction import load_manager, GalaxyManager
from tool.load import load_tool, GalaxyToolDefinition
from tool.tests import write_tests
from command.infer import infer_command, Command
from containers.fetch import fetch_container, Container
from janis.write_definition import write_janis

"""
this file parses a single tool to janis
the steps involved are laid out in order
each step involves a single module
only the tool module is called twice (load_tool, and write_tests)
"""

def parse_tool(args: dict[str, Optional[str]]):
    esettings: ToolExeSettings = load_tool_settings(args) 
    logger = Logger(esettings.get_logfile_path())
    try:
        gxmanager: GalaxyManager = load_manager(esettings)
        tool: GalaxyToolDefinition = load_tool(gxmanager)
        command: Command = infer_command(gxmanager, tool)
        container: Optional[Container] = fetch_container(esettings, logger, tool)
        write_janis(esettings, tool, command, container)
        write_tests(esettings, tool)
    except Exception as e:
        print(e)
        logger.log(2, 'parse_tool failed')
        


    

